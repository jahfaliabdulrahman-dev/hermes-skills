# Safetensors Inspection Without Torch

Read and verify safetensors model weights without needing PyTorch installed. Useful as a first-pass legitimacy check before setting up a full inference environment.

## Script

Save as `inspect_safetensors.py`:

```python
import json
import struct
import sys
import numpy as np

def read_safetensors(path):
    """Read safetensors file, return dict of {tensor_name: numpy_array}."""
    with open(path, 'rb') as f:
        header_len = struct.unpack('<Q', f.read(8))[0]
        header = json.loads(f.read(header_len))
        data_start = 8 + header_len
        tensors = {}
        for key, meta in header.items():
            if key == '__metadata__':
                continue
            offset = meta['data_offsets'][0] + data_start
            size = meta['data_offsets'][1] - meta['data_offsets'][0]
            shape = meta['shape']
            dtype_str = meta['dtype']
            f.seek(offset)
            raw = f.read(size)
            np_dtype = {'F32': np.float32, 'F16': np.float16, 'BF16': np.uint16,
                        'I64': np.int64, 'I32': np.int32, 'I8': np.int8,
                        'U8': np.uint8, 'F64': np.float64, 'BOOL': np.bool_}
            arr = np.frombuffer(raw, dtype=np_dtype.get(dtype_str, np.float32)).reshape(shape)
            tensors[key] = arr
    return tensors, header


def inspect(path):
    tensors, header = read_safetensors(path)
    total_params = sum(t.size for t in tensors.values())

    print(f"=== Safetensors Inspection: {path} ===")
    print(f"Total tensors: {len(tensors)}")
    print(f"Total parameters: {total_params:,}")

    # Show first 10 weight tensors with statistics
    print(f"\n{'Tensor':50s} {'Shape':20s} {'Mean':>10s} {'Std':>10s} {'Min':>10s} {'Max':>10s}")
    print("-" * 110)
    count = 0
    for name, arr in tensors.items():
        if count >= 10:
            break
        s = str(list(arr.shape))
        print(f"{name:50s} {s:20s} {arr.mean():10.6f} {arr.std():10.6f} {arr.min():10.6f} {arr.max():10.6f}")
        count += 1

    # Red flag checks
    print(f"\n--- Red Flag Checks ---")
    near_zero = sum(1 for t in tensors.values() for v in t.flatten()[:1000] if abs(v) < 1e-7)
    near_zero_pct = near_zero / (len(tensors) * 1000) * 100
    print(f"Near-zero fraction (sample): {near_zero_pct:.2f}% {'⚠️ HIGH' if near_zero_pct > 50 else '✅ OK'}")

    # Check for uniform values (untrained)
    uniform_count = 0
    for name, arr in tensors.items():
        if arr.std() < 1e-6 and arr.size > 1:
            uniform_count += 1
    print(f"Uniform/dead tensors: {uniform_count} {'⚠️ ' if uniform_count > len(tensors)*0.1 else '✅ OK'}")

    return total_params


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python inspect_safetensors.py <model.safetensors>")
        sys.exit(1)
    inspect(sys.argv[1])
```

## Quick One-Liner (no file save needed)

For a quick inline check from terminal:

```bash
python3 -c "
import json, struct, numpy as np
with open('model.safetensors', 'rb') as f:
    hl = struct.unpack('<Q', f.read(8))[0]
    h = json.loads(f.read(hl))
    ds = 8 + hl
total = 0
for k, m in h.items():
    if k != '__metadata__':
        total += int(np.prod(m['shape']))
print(f'Params: {total:,}')
"
```

## Common Pitfalls

- **LFS pointer stubs:** Hugging Face API returns size=0 for LFS-tracked files. This is expected. Always download the actual file to check.
- **Hugging Face download requires auth for gated models.** If curl returns HTML instead of binary, the model is gated — check if the repo mentions needing HF token.
- **bf16 tensors** (brain floating point) appear as `uint16` in the header. They cannot be directly interpreted as floats without conversion — flag these as "requires torch for full verification."
