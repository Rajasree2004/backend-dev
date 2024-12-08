# Top level package 

#appln name and version
__application__ = "task-tracker"
__version__ = "0.1.0"


#all possible errors
(
    SUCCESS,
    DIR_ERROR,
    FILE_ERROR,
    DB_READ_ERROR,
    DB_WRITE_ERROR,
    JSON_ERROR,
    ID_ERROR
) = range(7)


# map errors to human readable error messages
ERROR = {
    DIR_ERROR: "config directory error",
    FILE_ERROR: "config file error",
    DB_READ_ERROR: "database read error",
    DB_WRITE_ERROR: "database write error",
    ID_ERROR: "to-do id error"
}