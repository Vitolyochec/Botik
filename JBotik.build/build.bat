javac -d ./ Main.java
jar cfm JBotik.jar MANIFEST.MF ./JBotik/*.class icons/
java -jar JBotik.jar
pause