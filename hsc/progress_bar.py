from progress.bar import ChargingBar

class CustomProgress(ChargingBar):
	suffix = '%(percent)d%% [%(index)d/%(max)d]'
