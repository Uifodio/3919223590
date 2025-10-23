<?php
echo "<!DOCTYPE html>";
echo "<html><head><title>PHP Test</title></head>";
echo "<body>";
echo "<h1>PHP is working!</h1>";
echo "<p>Current time: " . date('Y-m-d H:i:s') . "</p>";
echo "<p>PHP Version: " . phpversion() . "</p>";
echo "<p>Server: " . $_SERVER['SERVER_SOFTWARE'] . "</p>";
echo "<p>Document Root: " . $_SERVER['DOCUMENT_ROOT'] . "</p>";
echo "</body></html>";
?>