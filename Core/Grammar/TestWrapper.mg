module Common
{
    import Language;
    import Microsoft.Languages;
    export Common;
    export Connectives;
    
    language Common
    {
        // Parameterized List rule        
        /*syntax List(element) 
            = n:element => [n] 
            | n:element l:List(element) => [n, valuesof(l)];
        
        syntax List(element, separator) 
            = n:element => [n] 
            | n:element separator l:List(element, separator) => [n, valuesof(l)];*/
            
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
        token TextSimple = ^(WhiteSpace);                    
    }
    
    language Connectives
    {
        @{Classification["Connective"]} token TIf = "if " | "if I";
        @{Classification["Connective"]} token TAll = " all ";
        @{Classification["Connective"]} token TOther = " the other" | "the other ";
        @{Classification["Connective"]} token TAnother = "another ";
        token TAnd = (' ')? "and" | (' ')? "and" (' ')? | (' ')? "and an" (' ')? | (' ')? "and a" (' ')? | "and";
        @{Classification["Connective"]} token TMany = "several " | "many ";
        token TA = " a " | " an ";
    }
}

module Setup
{
    import Language;
    import Microsoft.Languages;
    import Common;    
    export SetupLang;
    
    language SetupLang
    {
        
    }
}

module Test
{
    import Language;
    import Microsoft.Languages;
    import Setup;
    import Common;    
    export TestLanguage;
    
    language Asserts
    {
        syntax Constraints 
        = c:Constraint (".")?
        | cons:Constraints Connectives.TAnd c:Constraint (".")? => Constraints[valuesof(cons),c];
        
        syntax Constraint 
        = TConstraint p:TestLanguage.Property Connectives.TOther o:TestLanguage.Object
        => Constraint{Objects[o],Property[p]}
        | TConstraint p:TestLanguage.Property x:TestLanguage.Operators Connectives.TOther o:TestLanguage.Object
        => Constraint{Property{Name{p},o,x,Relation{"Reciprocal"}}}
        | TConstraint p:TestLanguage.Property x:TestLanguage.Operators v:TestLanguage.Value
        => Constraint{Property{Name{p},v,x}}
        | o:TestLanguage.Object TConstraint p:TestLanguage.Property x:TestLanguage.Operators v:TestLanguage.Value 
        => Constraint{Property{Name{p},v,o,x}};
        //| TConstraint TAll o:Object "'s" p:Property
        //=> [Property{p}]);
        
        token TConstraint = "should be" | "should" | "should have" | "should have";
    }
    
    language TestLanguage
    {    
        syntax Main = item:Test => [item]
        | list:Main item:Test => [valuesof(list),item];
        
        syntax Test = TTest title:Title ':' TSetupStart sp:SetupList TSetupEnd s:StatementList TEnd
        => Test{ Title{title}, sp, s };             
        
        syntax Title 
        = text:Common.SingleQuotedText => text;
        
        syntax StatementList = item:Statement => StatementList[item]
        | list:StatementList item:Statement => StatementList[valuesof(list), item];
        
        syntax Statement = 
        //a:CreateStatement => a
        | a:CreateMethodStatement => a
        //| a:IfStatement => a
        | a:WhenStatement => a;
        
        syntax SetupList = item:Setup => TypeList[item]
        | list:SetupList item:Setup => TypeList[valuesof(list),item];
        
        syntax Setup
            = o:Object prop:PropertyList sl:StatementList?
            => Type{o, prop, sl};
            
        syntax PropertyList = (' ')* TProperty item:Property => ProperyList[Property{Name{item}}]
        | list:PropertyList Connectives.TAnd? item:Property (".")? => PropertyList[valuesof(list), Property{Name{item}}]
        | (' ')* TProperty item:Property v:Value => ProperyList[Property{Name{item}, DefaultValue{v}}]
        | list:PropertyList Connectives.TAnd? item:Property v:Value (".")? => PropertyList[valuesof(list), Property{Name{item}, DefaultValue{v}}]
         | list:PropertyList Connectives.TAnd Connectives.TMany item:Property (".")? => PropertyList[valuesof(list), Property{Name{item}}]
        | (' ')* TProperty Connectives.TAnd? Connectives.TMany item:Property v:Value ('.')? => ProperyList[Property{Name{item}, DefaultValue{v}}]
        | list:PropertyList Connectives.TAnd? Connectives.TMany item:Property v:Value (".")? => PropertyList[valuesof(list), Property{Name{item}, DefaultValue{v}, Relation{"ManyToOne"}}];
            
        syntax WhenStatement 
            = TWhen o:Object m:Method Connectives.TAnother o2:Object"," TEach l:Loop"."
            => When{TargetMethod{Name{m}, Objects[o,o2], l}}
            | TWhen m:Method (Connectives.TAll|TEach|" ") o:Object TResult c:Asserts.Constraints
            => When{TargetMethod{Name{m}, Objects[o]}, c}
            | TWhen o:Object m:Method (Connectives.TAnother | "a") o2:Object"," c:Asserts.Constraints
            => When{TargetMethod{Name{m}, Objects[o,o2], c}};
            
        syntax CreateMethodStatement
            = TCreate m:Method Connectives.TAll o:Object "." 
            => CreateMethod{TargetMethod{Name{m},Objects[o]}}
            | TCreate o:Object TMethod m:Method Connectives.TAnother o2:Object "." 
            => CreateMethod{TargetMethod{Name{m},Objects[o,o2]}}
            | TCreate o:Object TMethod m:Method Connectives.TA o2:Object "." 
            => CreateMethod{TargetMethod{Name{m},Objects[o,o2]}}
            | TCreate m:Method o:Object p:Property"."
            => CreateMethod{TargetMethod{Name{m},Objects[o],Properties[Property{Name{p}}]}};
                   
        syntax Object = name:ObjectId => Object{Name{name}}
        | name:ObjectId v:Value => Object{Name{name}, Instance{v}};
        syntax Method = name:MethodId => name;
        syntax Property = name:PropertyId => name;
        syntax Value = " " '(' v:ValueId ')'=> Value{v}
        | '(' v:ValueId ')'=> Value{v}
        | '(' o:Object ')' => o;
        syntax Loop = o:Object c:Asserts.Constraints 
        => Loop{Objects[o],c};
        syntax Operators = x:TestLanguage.Equal | x:TestLanguage.Greater | x:TestLanguage.GreaterOrEqual | x:TestLanguage.Lesser | x:TestLanguage.LesserOrEqual
         => x;
        syntax Equal = TEqual => Operator{Value{"=="}};
        syntax Greater = TGreater => Operator{Value{">"}};
        syntax GreaterOrEqual = TGreaterOrEqual => Operator{Value{">="}};
        syntax Lesser = TLesser => Operator{Value{"<"}};
        syntax LesserOrEqual = TLesserOrEqual => Operator{Value{"<="}};
        
        token TEach = ("each " | " each " | "Each " | " Each ");
        token TCreate 
        = "I want a " 
        | "I want" TMethod;
        token TMethod = " to be able to " | " the ability to ";
        token TProperty = "To have " ("a"|"an") " ";
        token TEqual = " of " | "equal to " | " as ";
        token TGreater = " greater than ";
        token TGreaterOrEqual = " greater than or" TEqual;
        token TLesser = " less than ";
        token TLesserOrEqual = " less than or" TEqual;
        token TWhen = ("W"|"w")("hen " | "hen I " | "hen I" | "hen a ");
        
        token TResult = " the result ";
        @{Classification["Comment"]} token Comment = "//" (Base.Letter|'-'|'_'|' ')*+;
        
        @{Classification["TestOperator"]} token TTest = "begin story ";
        @{Classification["TestOperator"]} token TEnd = "end story";
        @{Classification["TestOperator"]} token TSetupStart = "begin setup ";
        @{Classification["TestOperator"]} token TSetupEnd = "end setup";
        @{Classification["Type"]} token ObjectId = '@' (Base.Letter|'-'|'_')+;
        @{Classification["Method"]} token MethodId = '#' (Base.Letter|'-'|'_')+;
        @{Classification["Property"]} token PropertyId = '~' (Base.Letter|'-'|'_')+;
        @{Classification["Value"]} token ValueId = (Base.Letter|'-'|'_'|Base.Digit|'.')+;
              
        syntax StringLiteral
          = val:Language.Grammar.TextLiteral => val;    
                       
        interleave whitespace = Common.WhiteSpace | CommentToken | '\t' | (' ');  
        //interleave Comment = CommentToken;  
        
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