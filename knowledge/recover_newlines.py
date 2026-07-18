import sys

path = '/opt/astro/runtime/event_predictor_v2.py'
content = open(path, 'r', encoding='utf-8').read()

print(f"File length: {len(content)}")
print("First 500 characters:")
print(content[:500])

# Count how many literal '\\n' we have
count = content.count('\\n')
print(f"Number of literal \\\\n sequences: {count}")

# Replace literal '\\n' with real newline '\n'
# Note: inside python, content.replace('\\n', '\n') does exactly this.
recovered = content.replace('\\n', '\n')

# Check if there are any syntax errors by trying to compile the recovered code
try:
    compile(recovered, '<string>', 'exec')
    print("Success: Recovered code compiles successfully with no syntax errors!")
    
    # Save the recovered code
    open(path, 'w', encoding='utf-8').write(recovered)
    print("Saved recovered file to /opt/astro/runtime/event_predictor_v2.py")
except Exception as e:
    print(f"Error compiling recovered code: {e}")
    # Write to a temp file for analysis
    temp_path = '/opt/astro/runtime/event_predictor_v2_recovered_debug.py'
    open(temp_path, 'w', encoding='utf-8').write(recovered)
    print(f"Saved debug file to {temp_path}")
