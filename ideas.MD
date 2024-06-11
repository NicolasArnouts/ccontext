- add an argument to specify documents like .pdfs, .jpgs, .... to add in a prompt -> u can only upload 10 files in 1 prompt, and there are rate limits regarding file uploads to OpenAI servers
- parse non txt files and/or add them to the clipboard -> same as, before max 10 in 1 prompt. Rate limits apply
- By default: add all binary files specified in "included" arg to the folder

NEW======

- When on ssh, notify user that the ssh connection should be started with -X, check if the user has a DISPLAY var by using:
```
echo $DISPLAY
```
