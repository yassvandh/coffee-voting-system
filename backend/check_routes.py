import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from app import app

print("URL Map:")
for rule in app.url_map.iter_rules():
    print(f"  {rule.rule}  {list(rule.methods)}")
