
def clean_data(x):
	return x.replace(",", " ") ##

test = "falsd;kfjasl;dkfjs;l 343423424332,,,,,,, 34343434343 j;lkjflkdjasflkdjfs;flj------"

print clean_data(test)

