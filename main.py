import asyncio
from pathlib import Path
from dotenv import load_dotenv
from deepagents import create_deep_agent
from deepagents.graph import init_chat_model
from deepagents.backends import LocalShellBackend

load_dotenv()


async def main():
    SYSTEM_PROMPT = (
        "You are a smart and highly autonomous software agent."
        "You must complete the entire task without asking any questions."
        "Always create and modify files using the filesystem backend."
        "All outputs must be written inside the directory: /Users/admin/Desktop/intern/gdp/merental-be-3/output2/yeet"
        "Rules you must follow:"
        "1. Never ask questions."
        "2. Always create real files, not pseudo code."
        "3. When running tests or tools, save logs and artifacts to the output directory."
        "4. If errors appear, fix the first error and rerun until stable."
        "5. If the task involves a development and testing loop, you must repeatedly implement, run, inspect, and fix until the result works correctly."
        "6. Do not stop early. Finish the full task."
        "7. Do not use screenshot or any image tool. Do not attach images to the model."
    )

    CONTENT = (
        "Stage, commit, push, and open a GitHub pull request for my current changes in this repo using gh."
        "Use description: 'add minor README update for yeet skill test'."
        "If I'm on main/master, create a branch named 'test/add-minor-readme-update-for-yeet-skill-test'."
        "Commit message should be 'add minor README update for yeet skill test' and PR title should be '[test] add minor README update for yeet skill test'."
        "Create the PR as draft and fill the body with a detailed explanation of what changed and how I validated it."
    )

    agent = create_deep_agent(
        model=init_chat_model("openai:gpt-5-mini"),
        backend=LocalShellBackend(
            root_dir=str(Path(__file__).parent.absolute()), inherit_env=True
        ),
        # skills=[".github/skills/"],
        system_prompt=f"{SYSTEM_PROMPT}",
    )

    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": f"{CONTENT}",
                }
            ],
        }
    )
    print(result["messages"][-1].content)


asyncio.run(main())
