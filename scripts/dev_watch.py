"""解决开发环境下，修改代码后 Windows 下无法自动重启服务器 ctrl + c 无效"""

# 1. 安装 watchfiles
# uv pip install watchfiles

# 2. 创建启动脚本
# dev_watch.py
import subprocess
import os
import sys
import time

from watchfiles import watch


def start_server() -> subprocess.Popen[bytes]:
    """启动服务器进程"""
    # ❯ uv run uvicorn app.server:app
    cmd = [
        # sys.executable,
        # "-m",
        "uv",
        "run",
        "uvicorn",
        "app.server:app",  # 修改为你的应用入口
    ]

    # cmd: list[str] = [
    #     "uv",
    #     "run",
    #     "langchain",
    #     "serve",  # 修改为你的应用入口
    # ]
    return subprocess.Popen(cmd)


def main():
    if sys.platform != "win32":
        print("此脚本仅适用于 Windows")
        sys.exit(1)

    print("🔍 启动文件监视开发服务器... 📁 ./app")
    print("🔄 检测到文件变化时自动重启 ⏸️  按 Ctrl+C 停止\n")

    process = start_server()

    def kill_port_windows(port):
        """Windows专用：终止占用端口的进程"""

        # 使用 netstat 查找进程ID
        cmd = f"netstat -ano | findstr :{port}"
        result = os.popen(cmd).read()

        # print(f"result: |{result}|")

        if not result:
            print(f"✅ 端口 {port} 未被占用")
            return

        pids = set()
        for line in result.strip().split("\n"):
            parts = line.strip().split()
            if len(parts) >= 5:
                pid = parts[-1]
                if pid.isdigit() and pid != "0":
                    pids.add(pid)

        # 终止找到的所有进程
        for pid in pids:
            print(f"    - 终止进程 {pid}")
            os.system(f"taskkill /F /PID {pid}")

        print(f"  ✅ 已终止占用 {port} 的进程 {len(pids)} 个")

    try:
        # 监视文件变化
        for changes in watch("./app", debounce=1500):  # 1.5秒防抖
            print(f"📝 检测到文件变化: {changes}")
            print("🔄 重启服务器...")

            # 终止旧进程
            print(f"  1. 终止旧进程 PID: {process.pid}")
            process.terminate()
            process.kill()

            process.wait()

            print("  2. 确认端口 8000 已释放")
            kill_port_windows(8000)
            # sleep 1 second to ensure the port is released
            time.sleep(1)

            # 启动新进程
            process = start_server()
            print("✅ 服务器已重启\n")

    except KeyboardInterrupt:
        print("\n🛑 停止服务器...")
        process.terminate()
        process.wait()
        print("👋 开发服务器已停止")


if __name__ == "__main__":
    main()
