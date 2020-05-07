from AnalyzerClass import *



if __name__ == '__main__':
	
	x = Analyzer()
	
	try:
		x.main()
		
	except KeyboardInterrupt:
		x.saveData()
		print("\n\nProgram is killed by KeyboardInterrupt event\n")
		print("ALL PROCESSED ITEMS WERE SAVED")
	'''
	except Exception as someException:
		print(someException)
		x.saveData()
		print("Some error occured during the procees...\nPlease, try again later...")
    '''
