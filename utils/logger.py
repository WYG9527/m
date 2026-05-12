import json
import os
from datetime import datetime

class Logger:
    def __init__(self, log_file: str = None):
        self.log_file = log_file or os.path.join(os.path.dirname(__file__), "data", "workflow_log.txt")
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)

    def log(self, agent: str, action: str, input_data: dict, output_data: dict):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent,
            "action": action,
            "input": input_data,
            "output": output_data
        }
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        return log_entry

    def get_workflow_history(self, student_id: str = None) -> list:
        if not os.path.exists(self.log_file):
            return []
        history = []
        with open(self.log_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    if student_id is None or entry.get("input", {}).get("student_id") == student_id:
                        history.append(entry)
                except:
                    continue
        return history

    def print_workflow(self, student_id: str = None):
        history = self.get_workflow_history(student_id)
        print("\n" + "="*70)
        print("Agent 工作流日志")
        print("="*70)
        for entry in history:
            print(f"\n⏰ {entry['timestamp']}")
            print(f"🤖 Agent: {entry['agent']}")
            print(f"📋 动作: {entry['action']}")
            print(f"📥 输入: {json.dumps(entry['input'], ensure_ascii=False, indent=2)}")
            print(f"📤 输出: {json.dumps(entry['output'], ensure_ascii=False, indent=2)[:500]}...")
        print("\n" + "="*70)