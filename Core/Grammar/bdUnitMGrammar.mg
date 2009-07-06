module Common
{
    import Language;
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

module Test
{
    import Language;
    import Common;
    import TestLanguage as TL;
    
    language Asserts
    {
        syntax Constraints 
        = c:Constraint
        | cons:Constraints Connectives.TAnd c:Constraint => Constraints[valuesof(cons),c];
        
        syntax Constraint 
        = TConstraint p:TL.Property Connectives.TOther o:TL.ConcreteClass
        => Constraint{ConcreteClasss[o],Property[p]}
        | TConstraint p:TL.Property x:TL.Operators Connectives.TOther o:TL.ConcreteClass
        => Constraint{Property{Name{p},o,x,Relation{"Reciprocal"}}}
        | TConstraint p:TL.Property x:TL.Operators v:TL.Value
        => Constraint{Property{Name{p},v,x}}
        | o:TL.ConcreteClass TConstraint p:TL.Property x:TL.Operators v:TL.Value 
        => Constraint{Property{Name{p},v,o,x}}
        | o:TL.ConcreteClass TConstraint x:TL.Operators o2:TL.ConcreteClass
        => Constraint{ConcreteClass[o, o2], x}
        | o:TL.ConcreteClass p1:TL.Property Asserts.TConstraint x:TL.Operators o2:TL.ConcreteClass p2:TL.Property
        => Constraint{ConcreteClassPropertyMapping{ConcreteClasses[o,o2],Properties[Property{Name{p1}},Property{Name{p2}}]}, x}
        | p:TL.Property TConstraint x:TL.Operators v:TL.Value
        => Constraint{Property{Name{p}, x, v}}
        | o:TL.ConcreteClass p:TL.Property TConstraint x:TL.Operators v:TL.Value
        => Constraint{Property{Name{p}, o, x, v}}
        | o:TL.ConcreteClass TConstraint c:TL.Count p:TL.Property
        => Constraint{Property{Name{p}, o, c}};
        
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
        a:CreateMethodStatement "."? => a
        | a:WhenStatement "."? => a;
        
        syntax SetupList = item:Setup "."? => TypeList[item]
        | list:SetupList item:Setup "."? => TypeList[valuesof(list),item];
        
        syntax Setup
            = o:ConcreteClass prop:PropertyList sl:StatementList?
            => Type{o, prop, sl};
            
        syntax PropertyList 
            = (' ')* TProperty item:Property => PropertyList[Property{Name{item}}]
            | list:PropertyList Connectives.TAnd? item:Property 
            => PropertyList[valuesof(list), Property{Name{item}}]
            | (' ')* TProperty item:Property v:Value 
            => PropertyList[Property{Name{item}, DefaultValue{v}}]
            | list:PropertyList Connectives.TAnd? item:Property v:Value 
            => PropertyList[valuesof(list), Property{Name{item}, DefaultValue{v}}]
            | list:PropertyList Connectives.TAnd Connectives.TMany item:Property
            => PropertyList[valuesof(list), Property{Name{item}}]
            | (' ')* TProperty Connectives.TAnd? Connectives.TMany item:Property v:Value 
            => ProperyList[Property{Name{item}, DefaultValue{v}}]
            | list:PropertyList Connectives.TAnd? Connectives.TMany item:Property v:Value 
            => PropertyList[valuesof(list), Property{Name{item}, DefaultValue{v}, Relation{"ManyToOne"}}];
           
            
        syntax WhenStatement 
            = TWhen tl:TargetList TEach l:Loop
            => When{tl, l}
            | TWhen tl:TargetList c:Asserts.Constraints Connectives.TAnd TEach l:Loop
            => When{tl, c, l}
            | TWhen tl:TargetList c:Asserts.Constraints
            => When{tl, c}
            | TWhen tl:TargetList if:IfStatement
            => When{tl, if};
            
        syntax IfStatement
            = "if" tl:TargetList "then" c:Asserts.Constraints
            => If{tl,Then{c}}
            | "if" tl:TargetList "then" c:Asserts.Constraints "else" c2:Asserts.Constraints
            => If{tl, Then{c}, Else{c2}}
            | "if" tl:TargetList "then" c:Asserts.Constraints "else" if:IfStatement
            => If{tl, Then{c}, Else{if}};

        syntax TargetList
            = item:Target (Connectives.TAnd | "," | ", the")?
            => TargetList[item]
            | list:TargetList Connectives.TAnd item:Target (Connectives.TAnd | "," | ", the")? 
            => TargetList[valuesof(list), item];

        syntax Target
            = m:Method (Connectives.TAll|TEach|" ") o:ConcreteClass TResult
            => Target{TargetMethod{Name{m}, ConcreteClasses[o]}}
            | o:ConcreteClass m:Method (Connectives.TAnother | " a ") o2:ConcreteClass
            => Target{TargetMethod{Name{m}, ConcreteClasses[o,o2]}}
            | o:ConcreteClass p:Property x:Operators v:Value
            => Target{TargetProperty{Name{p},ConcreteClasses[o], x, v}};
            
        syntax CreateMethodStatement
            = TCreate m:Method Connectives.TAll o:ConcreteClass
            => CreateMethod{TargetMethod{Name{m},ConcreteClasses[o]}}
            | TCreate o:ConcreteClass TMethod m:Method (Connectives.TAnother | Connectives.TA) o2:ConcreteClass
            => CreateMethod{TargetMethod{Name{m},ConcreteClasses[o,o2]}}
            | TCreate m:Method o:ConcreteClass p:Property
            => CreateMethod{TargetMethod{Name{m},ConcreteClasses[o],Properties[Property{Name{p}}]}}
            | TCreate m:Method Connectives.TA o:ConcreteClass
            => CreateMethod{TargetMethod{Name{m},ConcreteClasses[o]}}
            | TCreate o:ConcreteClass TMethod m:Method Connectives.TMany o2:ConcreteClass
            => CreateMethod{TargetMethod{Name{m},ConcreteClasses[o,o2], Relation{"ManyToOne"}}};
                   
        syntax ConcreteClass = name:ConcreteClassId => ConcreteClass{Name{name}}
        | name:ConcreteClassId v:Value => ConcreteClass{Name{name}, Instance{v}};
        syntax Method = name:MethodId => name;
        syntax Property = name:PropertyId => name;
        syntax Count = op:Operators? c:CountId => Count{Value{c}, op};
        syntax Value = " " '(' v:ValueId ')'=> Value{v}
        | '(' v:ValueId ')'=> Value{v}
        | '(' o:ConcreteClass ')' => o
        | '(' p:Property ')' => Value{p};
        syntax Loop = o:ConcreteClass c:Asserts.Constraints 
        => Loop{ConcreteClasses[o],c};
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
        token TProperty = "to have " ("a"|"an") " ";
        token TEqual = " of " | "equal to " | " as " | " is " | " the same as ";
        token TContains = " contain" "s"?;
        token TNotContains = "does"? " not contain";
        token TGreater = (" is"?) (" greater than " | " later than " | " more than ");
        token TGreaterOrEqual = (" is"?) (" greater than or" TEqual);
        token TLesser = (" is"?) (" less than " | " earlier than ");
        token TLesserOrEqual = (" is"?) (" less than or" TEqual);
        token TWhen = ("W"|"w")("hen " | "hen I " | "hen I" | "hen a ");
        
        token TResult = " the result ";
        @{Classification["Comment"]} token Comment = "//" (Base.Letter|'-'|'_'|' ')+;
        
        @{Classification["TestOperator"]} token TTest = "begin story ";
        @{Classification["TestOperator"]} token TEnd = "end story";
        @{Classification["TestOperator"]} token TSetupStart = "begin setup";
        @{Classification["TestOperator"]} token TSetupEnd = "end setup";
        @{Classification["Type"]} token ConcreteClassId = '@' (Base.Letter|'-'|'_')+;
        @{Classification["Method"]} token MethodId = '#' (Base.Letter|'-'|'_')+;
        @{Classification["Property"]} token PropertyId = '~' (Base.Letter|'-'|'_'|Base.Digit)+;
        @{Classification["Value"]} token ValueId = (Base.Letter|'_'|Base.Digit|'.')+ | Common.SingleQuotedText;
        token CountId = Base.Digit+;
              
        syntax StringLiteral = val:Language.Grammar.TextLiteral => val;    
                       
        interleave whitespace = Common.WhiteSpace | CommentToken | '\t'+ | ' ';  
        
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