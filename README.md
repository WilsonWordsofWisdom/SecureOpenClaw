# SecureOpenClaw
Additional security controls and safety guardrails md files for openclaw main workspace (for single agent setup)

Instructions:
1) run the following commands in your CLI:
      - ` git clone https://github.com/WilsonWordsofWisdom/SecureOpenClaw.git ~/guardrails-install && cd ~/guardrails-install && python3 install.py `

2) after installation is complete you can remove the temp folder using this command ` rm -rf ~/guardrails-install `

3) check diff / additional lines in AGENTS.md, SOUL.md, and HEARTBEAT.md files in your openclaw workspace folder, and that none of your original instructions in those md files were removed
  
4) if you accept the changes, navigate to your workspace folder to find the backup workspace folder and copy the name, you may then delete the backup original workspace folder using this command ` rm -rf ~/.openclaw/workspace_backup_<DATE>_<TIME> ` replacing the backup folder name with what you copied
   
6) chat with your openclaw bot using this prompt "I have additional several additional files and folders to your workspace folder to provide additional security controls and safety guardrails, please identify these files and diffs within existing md files, review them and flag anything that needs clarification. You may propose refinements to better refactor the changes to better integrate these mitigations with my current openclaw setup.
