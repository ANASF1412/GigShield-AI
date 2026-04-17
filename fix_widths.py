import os, glob

files = glob.glob('app_pages/*.py') + ['dashboard.py', 'ui/components.py']
for f in files:
    if os.path.exists(f):
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
        
        new_content = content.replace("width='stretch'", "use_container_width=True")
        new_content = new_content.replace('width="stretch"', "use_container_width=True")
        
        if new_content != content:
            with open(f, 'w', encoding='utf-8') as file:
                file.write(new_content)
            print(f"Fixed {f}")
