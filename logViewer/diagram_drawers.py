import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.table import Table

from statistic_queries import *


# def plot_connection_duration_histogram():
#     avg_duration = avg_good_connection_duration()
#     max_duration = max_good_connection_duration()
#     distribution = connection_duration_distribution()  # list of dicts with '_id' and 'count'
#
#     sorted_buckets = sorted(distribution, key=lambda x: (float('inf') if x['_id'] == "10k+" else x['_id']))
#
#     labels = []
#     boundaries = []
#
#     for i in range(len(sorted_buckets)):
#         current = sorted_buckets[i]['_id']
#
#         if current == "10k+" or current == float('inf'):
#             label = "10000+"
#         else:
#             next_bound = sorted_buckets[i + 1]['_id'] if i + 1 < len(sorted_buckets) and isinstance(sorted_buckets[i + 1]['_id'], (int, float)) else "∞"
#             label = f"{current}-{next_bound}" if isinstance(next_bound, (int, float)) else f"{current}+"
#
#         labels.append(label)
#         boundaries.append(current)
#
#     y_counts = [b['count'] for b in sorted_buckets]
#     x_ticks = list(range(len(labels)))
#
#     # Plotting
#     plt.figure(figsize=(12, 6))
#     bars = plt.bar(x_ticks, y_counts, color='skyblue', edgecolor='black')
#     # plt.bar(x_ticks, y_counts, color='skyblue', edgecolor='black')
#     plt.yscale('log')
#     plt.xticks(x_ticks, labels, rotation=45)
#     plt.xlabel('Connection Duration Ranges (ms)')
#     plt.ylabel('Number of Connections')
#     plt.title('Connection Duration Histogram')
#
#     plt.axvline(x=_find_bucket_index(avg_duration, sorted_buckets), color='green', linestyle='--', label=f'Avg: {avg_duration} ms')
#     plt.axvline(x=_find_bucket_index(max_duration, sorted_buckets), color='red', linestyle='--', label=f'Max: {max_duration} ms')
#
#     for bar, count in zip(bars, y_counts):
#         height = bar.get_height()
#         plt.text(bar.get_x() + bar.get_width() / 2 - 0.4, height, str(count),
#                  ha='left', va='bottom', fontsize=9, color='black')
#
#     plt.legend()
#     plt.tight_layout()
#
#     # Save and show
#     plt.savefig("graphs/connection_duration_histogram.png")
#     plt.show()


def plot_histogram_with_avg_max(distribution: list[dict], avg_value: int = None, max_value: int = None,
                                value_type: str = "Value", unit: str = "", output_path: str = "histogram.png",
                                title: str = "", xlabel: str = "", ylabel: str = "Count",
                                count_key: str = 'count'):
    """
    Generic histogram plotting function that supports avg/max vertical lines and bucket labels.

    Args:
        distribution: list of dicts like [{'_id': 0, 'count': 5}, ...]
        avg_value: numeric value to draw vertical line for average
        max_value: numeric value to draw vertical line for maximum
        value_type: Label for what's being measured (e.g. 'Connection Duration', 'Port Count')
        unit: Unit string to append to avg/max lines (e.g. 'ms')
        output_path: Where to save the plot
        title: Graph title
        xlabel: Label for x-axis
        ylabel: Label for y-axis
    """
    # Sort buckets
    sorted_buckets = sorted(distribution,
                            key=lambda x: (float('inf') if x['_id'] in ("∞", "10k+", float('inf')) else x['_id']))

    labels = []
    y_counts = [b[count_key] for b in sorted_buckets]
    boundaries = [b['_id'] for b in sorted_buckets]

    for i in range(len(boundaries)):
        current = boundaries[i]
        if current in ("10k+", "∞", float('inf')):
            label = f"{boundaries[i - 1]}+"
        else:
            next_bound = boundaries[i + 1] if i + 1 < len(boundaries) and isinstance(boundaries[i + 1],
                                                                                     (int, float)) else "∞"
            label = f"{current}-{next_bound}" if isinstance(next_bound, (int, float)) else f"{current}+"
        labels.append(label)

    x_ticks = list(range(len(labels)))

    plt.figure(figsize=(12, 6))
    bars = plt.bar(x_ticks, y_counts, color='skyblue', edgecolor='black')
    plt.yscale('log')
    plt.xticks(x_ticks, labels, rotation=45)
    plt.xlabel(xlabel or f'{value_type} Ranges {f"({unit})" if unit else ""}')
    plt.ylabel(ylabel)
    plt.title(title or f'{value_type} Histogram')

    def find_bucket_index(val):
        for i in range(len(boundaries)):
            lower = boundaries[i]
            upper = boundaries[i + 1] if i + 1 < len(boundaries) and isinstance(boundaries[i + 1],
                                                                                (int, float)) else float('inf')
            if isinstance(lower, (int, float)) and lower <= val < upper:
                return i
        return len(boundaries) - 1

    if avg_value is not None:
        plt.axvline(x=find_bucket_index(avg_value), color='green', linestyle='--', label=f'Avg: {float(avg_value):.2f}{unit}')
    if max_value is not None:
        plt.axvline(x=find_bucket_index(max_value), color='red', linestyle='--', label=f'Max: {max_value}{unit}')

    for bar, count in zip(bars, y_counts):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2 - 0.3, height, str(count),
                 ha='right', va='bottom', fontsize=9, color='black')

    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path)
    plt.show()


def _find_bucket_index(value, buckets):
    """
    Given a value, find its index in the sorted bucket list based on '_id' boundaries.
    """
    for i in range(len(buckets)):
        lower = buckets[i]['_id']
        upper = buckets[i + 1]['_id'] if i + 1 < len(buckets) and isinstance(buckets[i + 1]['_id'], (int, float)) else float('inf')
        if isinstance(lower, str):
            continue
        if lower <= value < upper:
            return i
    return len(buckets) - 1


def plot_hourly_data(hourly_data, title="Hourly Data", xlabel="Hour of Day", ylabel="Value", output_path=None):
    """
    Plots a bar chart of hourly data.

    Args:
        hourly_data (dict): Keys are hours (0-23), values are numeric.
        title (str): Chart title.
        xlabel (str): Label for X axis.
        ylabel (str): Label for Y axis.
        output_path (str|None): If given, save the plot image to this file path.
    """
    hours = list(range(24))
    values = [hourly_data.get(h, 0) for h in hours]

    plt.figure(figsize=(12, 6))
    plt.bar(hours, values, color='skyblue')
    plt.xticks(hours)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    if output_path:
        plt.savefig(output_path, bbox_inches='tight')

    plt.show()


def plot_connection_duration_histogram():
    avg_duration = avg_good_connection_duration()
    max_duration = max_good_connection_duration()
    distribution = connection_duration_distribution()

    plot_histogram_with_avg_max(
        distribution=distribution,
        avg_value=avg_duration,
        max_value=max_duration,
        value_type="Connection Duration",
        unit="ms",
        count_key="conn_count",
        output_path="graphs/connection_duration_histogram.png",
        title="Valid Connection Duration Histogram",
        xlabel="Duration Ranges (ms)",
        ylabel="Number of Connections"
    )


def plot_port_count_histogram():
    max_ports = max_no_ports_on_ip()
    avg_ports = avg_no_ports_on_ip()
    distribution = ip_port_count_distribution()

    plot_histogram_with_avg_max(
        distribution=distribution,
        avg_value=avg_ports,
        max_value=max_ports,
        value_type="Port Count",
        unit="",
        count_key="ip_count",
        output_path="graphs/port_count_histogram.png",
        title="Port Count Distribution per IP",
        xlabel="Number of Ports",
        ylabel="Number of IP's"
    )


def plot_total_bytes_conn_histogram():
    avg_bytes = average_bytes_per_connection()
    max_bytes = max_bytes_per_connection()
    distribution = ip_total_bytes_distribution()

    plot_histogram_with_avg_max(
        distribution=distribution,
        avg_value=avg_bytes,
        max_value=max_bytes,
        value_type="Bytes",
        unit=" bytes",
        count_key="conn_count",
        output_path="graphs/total_bytes_per_conn_histogram.png",
        title="Total Bytes per Connection Histogram",
        xlabel="Total Bytes Sent per Valid Connection",
        ylabel="Number of Connections"
    )


def plot_connection_count_histogram():
    distribution = ip_connection_count_distribution()
    avg_value = avg_conn_on_ip()
    max_value = max_conn_on_ip()
    unit = " connections"

    plot_histogram_with_avg_max(
        distribution=distribution,
        avg_value=avg_value,
        max_value=max_value,
        value_type="Connections",
        unit=" connections",
        count_key="ip_count",
        output_path="graphs/ip_connection_count_histogram.png",
        title="IP Connection Count Histogram",
        xlabel="Number of Connections per IP",
        ylabel="Number of IPs"
    )


def plot_connection_on_hour():
    hourly_averages = no_total_connections_on_hours()
    plot_hourly_data(hourly_averages,
                     title="Average Number of Connections per Hour",
                     ylabel="Avg Connections",
                     output_path="graphs/connections_per_hour.png")


def plot_no_valid_connections_on_hour():
    hourly_data = no_connections_on_hours()
    plot_hourly_data(
        hourly_data,
        title="Number of Valid Connections per Hour",
        ylabel="Valid Connections",
        output_path="graphs/valid_connections_per_hour.png"
    )


def plot_no_ips_on_hour():
    hourly_data = no_ips_on_hours()
    plot_hourly_data(
        hourly_data,
        title="Number of IPs per Hour",
        ylabel="Number of IPs",
        output_path="graphs/ips_per_hour.png"
    )


def plot_avg_bytes_on_hour():
    hourly_data = avg_bytes_on_hours()
    plot_hourly_data(
        hourly_data,
        title="Average Bytes per Hour",
        ylabel="Average Bytes",
        output_path="graphs/avg_bytes_per_hour.png"
    )


def plot_ips_per_country(ip_counts, output_path="graphs/ips_per_country.png"):
    count_to_countries = {}
    for country, count in ip_counts.items():
        count_to_countries.setdefault(count, []).append(country)

    sorted_counts = sorted(count_to_countries.keys(), reverse=True)

    labels = []
    widths = []
    heights = []
    for count in sorted_counts:
        countries = count_to_countries[count]
        labels.append("\n".join(countries))
        widths.append(count)
        heights.append(0.3 * len(countries))

    norm = mcolors.Normalize(vmin=min(widths), vmax=max(widths))
    cmap = plt.get_cmap('RdYlGn_r')  # reversed so green=low, red=high
    colors = [cmap(norm(w)) for w in widths]

    fig, ax = plt.subplots(figsize=(12, sum(heights) * 1.5))
    y_pos = []
    current_y = 0
    for h in heights:
        # center bars on cumulative position + half height
        y_pos.append(current_y + h / 2)
        current_y += h
    bars = ax.barh(y_pos, widths, height=heights, color=colors)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=11)
    ax.invert_yaxis()

    ax.set_xlabel('Number of IPs')
    ax.set_title('Number of IPs per Country')

    for bar in bars:
        width = bar.get_width()
        ax.text(width + max(widths) * 0.01, bar.get_y() + bar.get_height() / 2,
                str(width), va='center', fontsize=12, color='black')

    plt.tight_layout()
    plt.savefig(output_path)
    plt.show()


def plot_connections_per_country(connection_data, output_path="graphs/connections_per_country.png"):
    count_to_countries = {}
    for entry in connection_data:
        country = entry['_id']
        count = entry['total_connections']
        count_to_countries.setdefault(count, []).append(country)

    sorted_counts = sorted(count_to_countries.keys(), reverse=True)

    labels = []
    widths = []
    heights = []
    for count in sorted_counts:
        countries = count_to_countries[count]
        labels.append("\n".join(countries))
        widths.append(count)
        # bar height proportional to number of countries in group; adjust scale if needed
        heights.append(0.3 * len(countries))

    norm = mcolors.Normalize(vmin=min(widths), vmax=max(widths))
    cmap = plt.get_cmap('RdYlGn_r')  # green=low, red=high
    colors = [cmap(norm(w)) for w in widths]

    fig, ax = plt.subplots(figsize=(12, sum(heights) * 1.5))

    y_pos = []
    current_y = 0
    for h in heights:
        # center bars on cumulative position + half height
        y_pos.append(current_y + h / 2)
        current_y += h

    bars = ax.barh(y_pos, widths, height=heights, color=colors)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=11)
    ax.invert_yaxis()

    ax.set_xlabel('Total Connections')
    ax.set_title('Total Connections per Country')

    for bar, width in zip(bars, widths):
        ax.text(width + max(widths) * 0.01, bar.get_y() + bar.get_height() / 2,
                str(width), va='center', fontsize=12, color='black')

    plt.tight_layout()
    plt.savefig(output_path)
    plt.show()


def plot_connection_summary(total_conn, valid_conn, no_ips, output_path="graphs/connection_summary.png"):
    invalid_conn = total_conn - valid_conn
    categories = ['Number of IPs', 'Total Connections', 'Valid Connections', 'Invalid Connections']
    values = [no_ips, total_conn, valid_conn, invalid_conn]
    colors = ['purple', 'steelblue', 'forestgreen', 'indianred']

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(categories, values, color=colors)

    # Annotate values on bars
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, val + max(values) * 0.02,
                f'{val:,}', ha='center', va='bottom', fontsize=12)

    valid_pct = (valid_conn / total_conn) * 100 if total_conn else 0
    ax.text(bars[2].get_x() + bars[2].get_width() / 2, values[2] / 2,
            f'{valid_pct:.1f}%', ha='center', va='center', fontsize=12, color='white', fontweight='bold')
    ax.text(bars[3].get_x() + bars[3].get_width() / 2, values[3] / 2,
            f'{100-valid_pct:.1f}%', ha='center', va='center', fontsize=12, color='white', fontweight='bold')

    ax.set_ylabel('Count')
    ax.set_title('Connection Summary')
    ax.set_ylim(0, max(values) * 1.2)

    plt.tight_layout()
    plt.savefig(output_path)
    plt.show()


def plot_command_type_distribution():
    data = no_each_comm_type()

    labels = list(data.keys())
    sizes = list(data.values())

    legend_labels = [f"{label} ({count})" for label, count in zip(labels, sizes)]

    def make_autopct(values):
        def autopct(pct):
            total = sum(values)
            count = int(round(pct * total / 100.0))
            return f'{pct:.1f}%\n({count})'
        return autopct

    plt.figure(figsize=(8, 6))
    wedges, texts, autotexts = plt.pie(
        sizes,
        # labels=labels,
        autopct=make_autopct(sizes),
        startangle=140,
        textprops={'fontsize': 12}
    )

    plt.title('Command types distribution', fontsize=14)
    plt.axis('equal')

    plt.legend(wedges, legend_labels, title="Command Types", loc="center left", bbox_to_anchor=(1, 0.5))

    output_path = "graphs/comm_type_distr.png"
    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight')
    plt.show()


def plot_most_popular_usernames():
    data = n_most_popular_usernames()

    usernames = list(data.keys())
    frequencies = list(data.values())

    sorted_pairs = sorted(zip(usernames, frequencies), key=lambda x: x[1], reverse=True)
    usernames, frequencies = zip(*sorted_pairs)

    plt.figure(figsize=(8, 5))
    bars = plt.barh(usernames, frequencies, color='mediumseagreen')

    for bar, freq in zip(bars, frequencies):
        plt.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height() / 2,
                 str(freq), va='center', ha='left', fontsize=10)

    plt.title('Most used usernames')
    plt.xlabel('Appearances')
    plt.ylabel('Username')
    plt.gca().invert_yaxis()
    plt.tight_layout()

    output_path = 'graphs/most_used_usernames.png'
    plt.savefig(output_path)
    plt.show()


def plot_most_popular_passwords():
    data = n_most_popular_passwords()

    passwords = list(data.keys())
    frequencies = list(data.values())

    sorted_pairs = sorted(zip(passwords, frequencies), key=lambda x: x[1], reverse=True)
    usernames, frequencies = zip(*sorted_pairs)

    plt.figure(figsize=(8, 5))
    bars = plt.barh(usernames, frequencies, color='mediumseagreen')

    for bar, freq in zip(bars, frequencies):
        plt.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height() / 2,
                 str(freq), va='center', ha='left', fontsize=10)

    plt.title('Most used passwords')
    plt.xlabel('Appearances')
    plt.ylabel('Password')
    plt.gca().invert_yaxis()
    plt.tight_layout()

    output_path = 'graphs/most_used_passwords.png'
    plt.savefig(output_path)
    plt.show()


def plot_most_popular_commands_table():
    data = n_most_popular_commands()  # Assumes this returns a dict: {command_str: count}

    commands = list(data.keys())
    frequencies = list(data.values())

    # Sort by frequency descending
    sorted_data = sorted(zip(commands, frequencies), key=lambda x: x[1], reverse=True)

    fig, ax = plt.subplots(figsize=(10, 0.5 * len(sorted_data) + 1))
    ax.set_axis_off()

    # Create the table
    table_data = [["Command", "Frequency"]] + list(sorted_data)
    table = ax.table(cellText=table_data, colLabels=None, cellLoc='left', loc='center')

    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.5)

    plt.title("Most Popular Commands", fontsize=14, pad=20)

    output_path = "graphs/popular_commands_table.png"
    plt.savefig(output_path, bbox_inches="tight")
    plt.show()


def plot_all():
    plot_connection_duration_histogram()
    plot_port_count_histogram()
    plot_total_bytes_conn_histogram()
    plot_connection_count_histogram()

    plot_connection_on_hour()
    plot_no_valid_connections_on_hour()
    plot_no_ips_on_hour()
    plot_avg_bytes_on_hour()
    plot_ips_per_country(no_ips_on_country())
    plot_connections_per_country(no_connections_on_country())

    plot_connection_summary(no_total_connections(), no_good_connections(), no_ips())

    plot_command_type_distribution()
    plot_most_popular_usernames()
    plot_most_popular_passwords()
    plot_most_popular_commands_table()


if __name__ == '__main__':
    # plot_connection_duration_histogram()
    # plot_port_count_histogram()
    # plot_total_bytes_conn_histogram()
    # plot_connection_count_histogram()

    # plot_connection_on_hour()
    # plot_no_valid_connections_on_hour()
    # plot_no_ips_on_hour()
    # plot_avg_bytes_on_hour()
    # plot_ips_per_country(no_ips_on_country())
    # plot_connections_per_country(no_connections_on_country())
    #
    # plot_connection_summary(no_total_connections(), no_good_connections(), no_ips())
    #
    plot_command_type_distribution()
    plot_most_popular_usernames()
    plot_most_popular_passwords()
    plot_most_popular_commands_table()
