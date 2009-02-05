open (FILE, "$ARGV[0]");
open (WRFILE, ">$ARGV[1]");

for $line (<FILE>)
{    
    if ($line =~ /FullPath.{/)
    {
        print WRFILE "            FullPath = {\n";
    }
    else
    {
         print WRFILE "$line";
    }
}