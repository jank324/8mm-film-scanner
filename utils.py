import subprocess


def measure_cpu_temperature():
    out = subprocess.check_output(["vcgencmd", "measure_temp"]).decode("utf-8")
    temp = float(out.replace("temp=", "").replace("'C", ""))
    return temp
