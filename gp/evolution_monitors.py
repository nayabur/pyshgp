# _*_ coding: utf_8 _*_
"""
Created on 5/25/2016

@author: Eddie
"""

def best_total_error(population):
	return sorted(population, key=lambda ind: ind.get_total_error())[0].get_total_error()

def average_total_error(population):
	return sum(map(lambda ind: ind.get_total_error(), population)) / len(population)

def average_genome_size(population):
	return sum(map(lambda ind: len(ind.get_genome()), population)) / len(population)

def smallest_genome_size(population):
	return min(map(lambda ind: len(ind.get_genome()), population))

def largest_genome_size(population):
	return max(map(lambda ind: len(ind.get_genome()), population))

def unique_genome_count(population):
	return -1

#

def print_monitors(population, monitors_dict):
	'''
	Prints all of the values the user asked to monitor in monitors_dict
	'''
	if monitors_dict["best_total_error"]:
		print "Best Total Error:", best_total_error(population)
	if monitors_dict["average_total_error"]:
		print "Average Total Error:", average_total_error(population)
	if monitors_dict["average_genome_size"]:
		print "Average Genome Size:", average_genome_size(population)
	if monitors_dict["smallest_genome_size"]:
		print "Smallest Genome Size:", smallest_genome_size(population)
	if monitors_dict["largest_genome_size"]:
		print "Largest Genome Size:", largest_genome_size(population)
	if monitors_dict["unique_genome_count"]:
		print "Number of Unique Genomes:", unique_genome_count(population)