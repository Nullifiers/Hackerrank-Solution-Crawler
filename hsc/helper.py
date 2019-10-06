import sys
from hsc import color

Color = color.Color


def update_progress(index, total, challenge_name):
    """Show update progress for index out of total"""
    bar_length = 30
    status = ""
    progress = index / total
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
        status = "error: progress var must be float\r\n"
    if progress < 0:
        progress = 0
        status = "Halt...\r\n"
    if progress >= 1:
        progress = 1
        status = "Done...\r\n"
        challenge_name = ""
    block = int(round(bar_length * progress))
    text = "\rCrawling your hackerrank solutions: {0}[{1}]{2} {3}% [{4}/{5}] {6} {7}".format(
        Color.BLUE, "="*block + "-"*(bar_length - block), Color.END, int(progress*100),
        index, total, challenge_name, status)
    sys.stdout.write(text)
    sys.stdout.flush()

