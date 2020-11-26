# USCISTracker

USCISTracker is a tool which can check the status of a batch of cases.

Usage:

1. Set the variable myCase to your case number. The default is MSC2090000000

2. Set the monitorNumber. The default is -100. It means check the cases which were filed before yours case with the same form type.

3. Run the command:

    > python USCISTracker.py
    
    The first time, it will download all the cases and save them to a file. The file name is <case name>.cache. For example, your case number is MSC2090000000, the file name will be MSC2090000000.cache.
  
    when run this command again, it will only check the saved cases status. If it is changed, the information will be printed out.
