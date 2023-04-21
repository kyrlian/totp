diconame="./dicos/words_fr.txt"
dicofile=open(diconame, 'r')
dicolist=dicofile.readlines()
dicolist.sort()
dicofile.close()
newfile=open(diconame,'w')
oldword=''
wordlist=[]
while len(dicolist)>0:
	word=dicolist.pop()
	if word!=oldword:
		if len(word)>1:
			newfile.write(word)
		oldword=word
newfile.close()
