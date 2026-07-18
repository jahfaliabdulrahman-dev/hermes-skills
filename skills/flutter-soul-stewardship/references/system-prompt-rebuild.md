# System Prompt Rebuild — Python Procedure

When a profile's `config.yaml` `agent.system_prompt` is truncated or missing recent SOUL sections, use this Python procedure to rebuild it.

## Why This Happens

Sections are added to SOUL.md over time. The config.yaml `agent.system_prompt` is a YAML string that was manually embedded once — it doesn't auto-sync with SOUL.md. When new sections are added to SOUL.md, they must also be appended to the system_prompt.

## Rebuild Procedure

```python
import yaml

config_path = "/Users/abdurrahmanjahfali/.hermes/profiles/<profile-name>/config.yaml"

# 1. Read current config
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

current = config['agent']['system_prompt']

# 2. Read the canonical SOUL.md
soul_path = config_path.replace('config.yaml', 'SOUL.md')
with open(soul_path, 'r') as f:
    soul_content = f.read()

# 3. Check what SOUL sections are MISSING from system_prompt
sections = [
    'Soul Stewardship',
    'Worker Output Validation', 
    'Known-Bug Enforcement',
    'Stub Detection Gate',
    'Source Control for Workers'
]

for section in sections:
    if section not in current:
        print(f"MISSING: {section}")
        # Extract this section from SOUL.md and append to current
        # (complex — may need manual construction)

# 4. Write back with yaml.dump
with open(config_path, 'w') as f:
    yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False, width=200)

# 5. Verify
with open(config_path, 'r') as f:
    config2 = yaml.safe_load(f)
for section in sections:
    assert section in config2['agent']['system_prompt'], f"FAILED: {section} not in rebuilt prompt"

print(f"System prompt rebuilt: {len(config2['agent']['system_prompt'])} chars")
```

## YAML Escaping Reference

When building system_prompt strings manually:
- `\n` → newline in YAML double-quoted strings
- `\u2014` → em dash (—)
- `\u00a7` → section sign (§)
- `\"` → literal double quote
- `\\` → literal backslash

## Verification After Rebuild

```bash
# Check key config values survived
python3 -c "
import yaml
with open('config.yaml') as f:
    c = yaml.safe_load(f)
print('model:', c['model']['default'])
print('provider:', c['model']['provider'])
print('max_turns:', c['agent']['max_turns'])
print('system_prompt length:', len(c['agent']['system_prompt']))
"
```
