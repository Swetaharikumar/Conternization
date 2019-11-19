download:
	mkdir -p base_images
	wget -P base_images/ http://www.andrew.cmu.edu/user/ayushagr/basefs.tar.gz

install:
	# Put any compilation instructions here if required
	# Any third party installations shuld also occur here

manager:
	python Manager.py

clean:
	sudo rm -rf configfiles/
	sudo rm -rf containers/
	# sudo rm -rf launched_images/

cli_tests: sudo clean
	./grading/cli_tests/test_1_upload.sh
	./grading/cli_tests/test_2_cfginfo.sh
	./grading/cli_tests/test_3_launch.sh
	./grading/cli_tests/test_4_list.sh
	./grading/cli_tests/test_5_destroyall.sh

api_tests: clean
	python3 grading/rest/grading.py 

	
	
