@echo off

echo [BUILDING JBotik]

@echo on

javac -d ./classes Main.java
jar cfm JBotik.jar MANIFEST.MF icons/ fonts/ -C classes .
java -jar JBotik.jar

pause
