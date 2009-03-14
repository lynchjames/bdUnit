module Common
{
    import Language;
    import Microsoft.Languages;
    export Common;
    export Connectives;
    
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
        => Constraint{Property{Name{p},v,o,x}}
        | o:TestLanguage.Object TConstraint x:TestLanguage.Operators o2:TestLanguage.Object
        => Constraint{Objects[o, o2], x}
        | p:TestLanguage.Property TConstraint x:TestLanguage.Operators v:TestLanguage.Value
        => Constraint{Property{Name{p}, x, v}}
        | o:TestLanguage.Object p:TestLanguage.Property TConstraint x:TestLanguage.Operators v:TestLanguage.Value
        => Constraint{Property{Name{p}, o, x, v}};
        //| TConstraint TAll o:Object "'s" p:Property
        //=> [Property{p}]);
        
        token TConstraint = ' '? ("should be" | "should" | "should have" | "should have");
    }
    
    language TestLanguage
    {    
        syntax Main = item:Test => [item]
        | list:Main item:Test => [valuesof(list),item];
        
        syntax Test = TTest title:Title ':' TSetupStart sp:SetupList TSetupEnd s:StatementList TEnd
        => Test{ Title{title}, sp, s}
        | TTest title:Title ':' TSetupStart sp:SetupList TSetupEnd TEnd
        => Test{ Title{title}, sp}
        | TTest title:Title ':' s:StatementList TEnd
        => Test{ Title{title}, s};
        
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
            = TWhen tl:TargetList TEach l:Loop"."?
            => When{tl, l}
            | TWhen tl:TargetList c:Asserts.Constraints
            => When{tl, c};

        syntax TargetList
        = item:Target (Connectives.TAnd | "," | ", the")? => TargetList[item]
        | list:TargetList Connectives.TAnd item:Target (Connectives.TAnd | "," | ", the")? => TargetList[valuesof(list), item];

        syntax Target
        = m:Method (Connectives.TAll|TEach|" ") o:Object TResult
        => Target{TargetMethod{Name{m}, Objects[o]}}
        | o:Object m:Method (Connectives.TAnother | " a ") o2:Object
        => Target{TargetMethod{Name{m}, Objects[o,o2]}}
        | o:Object p:Property x:Operators v:Value
        => Target{TargetProperty{Name{p},Objects[o], x, v}};
            
        syntax CreateMethodStatement
            = TCreate m:Method Connectives.TAll o:Object
            => CreateMethod{TargetMethod{Name{m},Objects[o]}}
            | TCreate o:Object TMethod m:Method Connectives.TAnother o2:Object
            => CreateMethod{TargetMethod{Name{m},Objects[o,o2]}}
            | TCreate o:Object TMethod m:Method Connectives.TA o2:Object 
            => CreateMethod{TargetMethod{Name{m},Objects[o,o2]}}
            | TCreate m:Method o:Object p:Property
            => CreateMethod{TargetMethod{Name{m},Objects[o],Properties[Property{Name{p}}]}};
                   
        syntax Object = name:ObjectId => Object{Name{name}}
        | name:ObjectId v:Value => Object{Name{name}, Instance{v}};
        syntax Method = name:MethodId => name;
        syntax Property = name:PropertyId => name;
        syntax Value = " " '(' v:ValueId ')'=> Value{v}
        | '(' v:ValueId ')'=> Value{v}
        | '(' o:Object ')' => o
        | '(' p:Property ')' => Value{p};
        syntax Loop = o:Object c:Asserts.Constraints 
        => Loop{Objects[o],c};
        syntax Operators = x:Equal | x:Contains | x:NotContains | x:Greater | x:GreaterOrEqual | x:Lesser | x:LesserOrEqual
         => x;
        syntax Equal = TEqual => Operator{Value{"=="}};
        syntax Contains = TContains => Operator{Value{"contains"}};
        syntax NotContains = TNotContains => Operator{Value{"notcontains"}};
        syntax Greater = TGreater => Operator{Value{">"}};
        syntax GreaterOrEqual = TGreaterOrEqual => Operator{Value{">="}};
        syntax Lesser = TLesser => Operator{Value{"<"}};
        syntax LesserOrEqual = TLesserOrEqual => Operator{Value{"<="}};
        
        token TEach = ("each " | " each " | "Each " | " Each ");
        token TCreate 
        = "I want a " 
        | "I want" TMethod;
        token TMethod = " to be able to " | " the ability to ";
        @{CaseSensitive[false]}
        token TProperty = "to have " ("a"|"an") " ";
        token TEqual = " of " | "equal to " | " as " | " is ";
        token TContains = " contain" "s"?;
        token TNotContains = " not contain";
        token TGreater = " greater than " | " later than ";
        token TGreaterOrEqual = " greater than or" TEqual;
        token TLesser = " less than " | " earlier than ";
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
        @{Classification["Value"]} token ValueId = (Base.Letter|'_'|Base.Digit|'.')+ | Common.SingleQuotedText;
              
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