# BEACON Toolkit
# July 2012
#
# Two helper functions to augment DataFrame objects with 
# new rows or columns. 
#
# By: Luis Zaman and Brian Connelly

# Add a new entry to a DataFrame
# Parameters:
#   dataframe - the dataset to augment
#   row - a vector containing the entry to add, it must be the same size as 
#         the dataframe
add_row <- function(dataframe, row)
{
	if(length(row) == length(dataframe))
	{
		# add the new row to the end of the DataFrame
		new_row_index <- length(dataframe[,1]) + 1
		dataframe[new_row_index, ] <- row
	}
	else
	{
		print("Row length differs from DataFrame length")
		dataframe <- NULL
	}
	return(dataframe)
}

# Add a new column to a DataFrame
# Parameters:
#   dataframe - the dataset to augment
#   column - a vector containing the new column's data, must have the same number
#            of elements as the other columns
#   column_header - the name to give this new column (defaults to NewColumn)
add_column <- function(dataframe, column, column_header="NewColumn")
{
	if(length(column) == length(dataframe[,1]))
	{
		dataframe[column_header] <- column
	}
	else
	{
		print("Column length differs from DataFrame size")
		dataframe <- NULL
	}
	return(dataframe)
}