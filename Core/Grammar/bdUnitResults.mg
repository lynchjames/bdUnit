module Common
{
    import Language;
    export Common;
    
    language Common
    {            
        @{Classification["String"]} 
        token SingleQuotedText = QuotedText('"');
        token DoubleQuotedText = QuotedText("'");
        
        token Comment = Base;
        
        // From M.mg
        token QuotedText(Q) = Q (TextSimple - Q)* Q;
        // No reason to exclude backslash
        token WhiteSpace = '\u000A' // New Line
              | '\u000D' // Carriage Return
              | '\u0085' // Next Line
              | '\u2028' // Line Separator
              | '\u2029' // Paragraph Separator
              | '\t'
              | '\u0009'; // Tab
        
        @{Classification["text"]}
        token TextSimple = ^(WhiteSpace);                    
    }
}

module Test
{
    import Language;
    import Common;
    import TestLanguage as TL;
    
    @{CaseInsensitive}
    language TestLanguage
    {    
        syntax Main = item:Test => [item]
        | list:Main item:Test => [valuesof(list),item];
        
        syntax Test = TTest title:Title ':' TSetupStart t:Text TSetupEnd s:StatementList TEnd
        => Test{ Title{title}, s}
        | TTest title:Title ':' TSetupStart t:Text TSetupEnd TEnd
        => Test{ Title{title}}
        | TTest title:Title ':' s:StatementList TEnd
        => Test{ Title{title}, s};
        
        syntax Title 
        = text:Common.SingleQuotedText => text;
        
        syntax StatementList = item:Statement => StatementList[item]
        | list:StatementList item:Statement => StatementList[valuesof(list), item];
        
        syntax Statement = a:WhenStatement "."? => a;
            
        syntax WhenStatement 
            = TWhen text:StringLiteral
            => When{text};
                   
        token TWhen = ("W"|"w")("hen " | "hen I " | "hen I" | "hen a ");
        
        @{Classification["TestOperator"]} token TTest = "begin story ";
        @{Classification["TestOperator"]} token TEnd = "end story";
        @{Classification["TestOperator"]} token TSetupStart = "begin setup ";
        @{Classification["TestOperator"]} token TSetupEnd = "end setup";
        
        syntax StringLiteral = val:Language.Grammar.TextLiteral => val; 
        
        syntax Text = s:StringLiteral | t:Common.TextSimple | whitespace;
                       
        interleave whitespace = Common.WhiteSpace | CommentToken | '\t' | (' ');  
        
        @{Classification["Comment"]}
        token CommentToken 
            = CommentDelimited
            | CommentLine;
        token CommentDelimited = "/*" CommentDelimitedContent* "*/";
        token CommentDelimitedContent = 
            ^('*')
            | '*'  ^('/');
        token CommentLine = "//" CommentLineContent*;
                token CommentLineContent = ^(
                 '\u000A' // New Line
              |  '\u000D' // Carriage Return
              |  '\u0085' // Next Line
              |  '\u2028' // Line Separator
              |  '\u2029'); // Paragraph Separator    
    }
}