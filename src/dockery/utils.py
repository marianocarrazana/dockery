def get_cpu_usage(stats: dict) -> float:
    cpu_stats = stats["cpu_stats"]
    precpu_stats = stats["precpu_stats"]
    delta = (
        cpu_stats["cpu_usage"]["total_usage"] - precpu_stats["cpu_usage"]["total_usage"]
    )
    system_delta = cpu_stats.get("system_cpu_usage", 0) - precpu_stats.get(
        "system_cpu_usage", 0
    )
    len_cpu = cpu_stats.get("online_cpus", 1)

    if system_delta == 0:
        return 0.0

    percentage = (delta / system_delta) * len_cpu * 100
    return percentage


def get_mem_usage(stats: dict) -> float:
    mem_stats = stats["memory_stats"]
    if len(mem_stats) == 0:
        return 0.0
    mem_used = (
        mem_stats["usage"]
        - mem_stats["stats"].get("cache", 0)
        + mem_stats["stats"]["active_file"]
    )
    limit = stats["memory_stats"]["limit"]
    percentage = mem_used / limit * 100
    return percentage
