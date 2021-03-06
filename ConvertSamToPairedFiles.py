#!/usr/bin/env python
# encoding= utf-8
# author: Sébastien Boisvert

import sys

def reverse(sequence):
	reverseSequence=""
	i=len(sequence)-1
	while i>=0:
		reverseSequence+=sequence[i]
		i-=1
	return reverseSequence

def complementSymbol(symbol):
	if symbol=='A':
		return 'T';
	if symbol=='T':
		return 'A';
	if symbol=='G':
		return 'C';
	if symbol=='C':
		return 'G';
	return symbol;

def complement(sequence):
	i=0
	maximum=len(sequence)
	output=""
	while i<maximum:
		output+=complementSymbol(sequence[i])
		i+=1

	return output

def reverseComplement(sequence):
	return reverse(complement(sequence))

def writeSequence(file,name,sequence,quality):
	file.write("@"+name+"\n"+sequence+"\n+\n"+quality+"\n")

arguments=sys.argv


offsetForProgram=0
offsetForSamFile=1
offsetForOutputPrefix=2
offsetForSequencesPerFile=3


if len(arguments)!=4:
	print("Convert a sam file to paired fastq files")
	print("Author: Sébastien Boisvert")
	print("Usage:")
	print(arguments[offsetForProgram]+" samFile outputPrefix sequencesPerFile")
	sys.exit(1)

columnForQueryName=1
columnForSequence=10
columnForQuality=11


samFile=arguments[offsetForSamFile]
outputPrefix=arguments[offsetForOutputPrefix]
sequencesPerFile=int(arguments[offsetForSequencesPerFile])

stream=open(samFile)

store={}

leftFile=None
rightFile=None
singleFile=None

pairs=0
part=0

total=0

for line in stream:

	if total%1000==0:
		sys.stdout.write("\r"+str(total))

	total+=1

	columns=line.split("\t")

	if columns[0]=='@SQ' or columns[0]=='@PG':
		continue

	queryName=columns[columnForQueryName-1]
	sequence=columns[columnForSequence-1]
	quality=columns[columnForQuality-1].strip()

	if queryName not in store:
		store[queryName]=[sequence,quality]
		continue
	else:
		if leftFile==None:
			leftFile=open(outputPrefix+"."+str(part)+"._1.fastq","w")
			rightFile=open(outputPrefix+"."+str(part)+"._2.fastq","w")

		writeSequence(leftFile,queryName+"/1",store[queryName][0],store[queryName][1])
		del store[queryName]
		writeSequence(rightFile,queryName+"/2",reverseComplement(sequence),reverse(quality))
		pairs+=1

		if pairs==sequencesPerFile:
			leftFile.close()
			leftFile=None
			rightFile.close()
			rightFile=None
			pairs=0
			part+=1

stream.close()


names=store.keys()

part=0
processed=0
singleFile=None

for queryName in names:
	if singleFile==None:
		singleFile=open(outputPrefix+"."+str(part)+".fastq","w")

	writeSequence(singleFile,queryName,store[queryName][0],store[queryName][1])
	del store[queryName]
	processed+=1

	if processed==sequencesPerFile:
		singleFile.close()
		singleFile=None
		processed=0
		part+=1


sys.stdout.write("\n")
