#region Using Statements

using System.Collections.Generic;
using bdUnit.Core;
using NUnit.Framework;

#endregion

namespace bdUnit.Tests
{
    [TestFixture]
    public class PrototypeTests
    {
        #region Text

        private string _input =
            @"begin story ""LogansRun_Marriage"":
    //I want a @User to have a ~Spouse and a ~IsARunner and an ~Age.
    I want a @User to be able to #Marry another @User.
    I want to be able to #Total all @User's.
    When a @User #Marry's another @User each @User should be ~Spouse as the other @User and should have ~IsARunner equal to (false) and should have ~Age equal to (30).
    I want to be able to #Total @User ~Age.
end story

begin story ""THE_RETURN"":
    I want a @User to be able to #Marry another @User.
    I want to be able to #Total all @User's.
end story";

        private const string _grammar =
            @"module APE
                {
                    import Language;
                    import Microsoft.Languages;

                    language Common
                    {
                        // Parameterized List rule        
                        /*syntax List(element) 
                            = n:element => [n] 
                            | n:element l:List(element) => [n, valuesof(l)];
                        
                        syntax List(element, separator) 
                            = n:element => [n] 
                            | n:element separator l:List(element, separator) => [n, valuesof(l)];*/
                            
                        @{Classification[""String""]} 
                        token SingleQuotedText = QuotedText('""');
                        token DoubleQuotedText = QuotedText(""'"");
                        
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
                    
                    language Asserts
                    {
                        syntax Constraints 
                        = c:Constraint
                        | cons:Constraints Connectives.TAnd c:Constraint => Constraints[valuesof(cons),c];
                        
                        syntax Constraint 
                        = TConstraint p:TestLanguage.Property Connectives.TOther o:TestLanguage.Object
                        => Constraint{Objects[o],Property[p]}
                        | TConstraint p:TestLanguage.Property e:TestLanguage.Equal Connectives.TOther o:TestLanguage.Object
                        => Constraint{Property{Name{p},o,Operator{e}}}
                        | TConstraint p:TestLanguage.Property e:TestLanguage.Equal v:TestLanguage.Value
                        => Constraint{Property{Name{p},v,Operator{e}}};
                        //| TConstraint TAll o:Object ""'s"" p:Property
                        //=> [Property{p}]);
                        
                        token TConstraint = """" should be """" | """" should """" | "" should have "";
                    }
                    
                    language Connectives
                    {
                        @{Classification[""Connective""]} token TIf = ""if "" | ""if I"";
                        @{Classification[""Connective""]} token TAll = "" all "";
                        @{Classification[""Connective""]} token TOther = "" the other "" | ""the other "";
                        @{Classification[""Connective""]} token TAnother = "" another "";
                        token TAnd = "" and"";
                    }
                    
                    language TestLanguage
                    {    
                        syntax Main = item:Test => [item]
                        | list:Main item:Test => [valuesof(list),item];
                        
                        syntax Test = TTest title:Title ':' s:StatementList TEnd
                        => Test{ Title{title}, s };             
                        
                        syntax Title 
                        = text:Common.SingleQuotedText => text;
                        
                        syntax StatementList = (' ')* item:Statement => StatementList[item]
                        | list:StatementList (' ')* item:Statement => StatementList[valuesof(list), item];
                        
                        syntax Statement = 
                        //a:CreateStatement => a
                        | a:CreateMethodStatement => a
                        //| a:IfStatement => a
                        | a:WhenStatement => a;                        
                            
                        syntax WhenStatement 
                            = TWhen o:Object "" "" m:Method ""'s"" Connectives.TAnother o2:Object TEach l:Loop"".""
                            => When{TargetMethod{Name{m}, Objects[o,o2], l}}
                            | TWhen m:Method (Connectives.TAll|TEach|"" "") o:Object""'s,"" TResult c:Asserts.Constraint
                            => When{TargetMethod{Name{m}, Objects[o], c}};
                        //syntax CreateStatement 
                            
                        syntax CreateMethodStatement
                            = TCreate m:Method "" all "" o:Object ""'s."" 
                            => CreateMethod{TargetMethod{Name{m},Objects[o]}}
                            | TCreate o:Object TMethod m:Method Connectives.TAnother o2:Object ""."" 
                            => CreateMethod{TargetMethod{Name{m},Objects[o,o2]}}
                            | TCreate m:Method "" "" o:Object "" "" p:Property"".""
                            => CreateMethod{TargetMethod{Name{m},Objects[o],PropertyList[{p}]}};
                                   
                        syntax Object = name:ObjectId => Object{name};
                        syntax Method = name:MethodId => name;
                        syntax Property = name:PropertyId => name;
                        syntax Value = '('v:ValueId ')'=> Value{v};
                        syntax Loop = o:Object c:Asserts.Constraints 
                        => Loop{Objects[o],c};
                        syntax Equal = TEqual => ""equality"";
                        
                        token TEach = (""each "" | "" each "" | ""Each "" | "" Each "");
                        token TCreate 
                        = ""I want a "" 
                        | ""I want"" TMethod;
                        token TMethod = "" to be able to "" | "" the ability to "";
                        
                        token TEqual = "" of "" | "" equal to "" | "" as "";
                        token TWhen = (""W""|""w"")(""hen "" | ""hen I "" | ""hen I"" | ""hen a "");
                        
                        token TResult = "" the result "";
                        @{Classification[""Comment""]} token Comment = ""//"" (Base.Letter|'-'|'_'|' ')*+;
                        
                        @{Classification[""TestOperator""]} token TTest = ""begin story "";
                        @{Classification[""TestOperator""]} token TEnd = ""end story"";
                        @{Classification[""GenerateType""]} token ObjectId = '@' (Base.Letter|'-'|'_')+;
                        @{Classification[""Method""]} token MethodId = '#' (Base.Letter|'-'|'_')+;
                        @{Classification[""Property""]} token PropertyId = '~' (Base.Letter|'-'|'_')+;
                        @{Classification[""Value""]} token ValueId = (Base.Letter|'-'|'_'|Base.Digit)+;
                              
                        syntax StringLiteral
                          = val:Language.Grammar.TextLiteral => val;    
                                       
                        interleave whitespace = Common.WhiteSpace | CommentToken | '\t';  
                        //interleave Comment = CommentToken;  
                        
                        @{Classification[""Comment""]}
                        token CommentToken 
                            = CommentDelimited
                            | CommentLine;
                        token CommentDelimited = ""/*"" CommentDelimitedContent* ""*/"";
                        token CommentDelimitedContent = 
                            ^('*')
                            | '*'  ^('/');
                        token CommentLine = ""//"" CommentLineContent*;
                                token CommentLineContent = ^(
                                 '\u000A' // New Line
                              |  '\u000D' // Carriage Return
                              |  '\u0085' // Next Line
                              |  '\u2028' // Line Separator
                              |  '\u2029'); // Paragraph Separator    
                    }
                }";

        #endregion

        [Test]
        public void LogansRun_WithFile()
        {
            var paths = new Dictionary<string, string>();
            paths["input"] = "../../../Core/Inputs/LogansRun.input";
            paths["grammar"] = "../../../Core/Grammar/TestWrapper.mg";
            var parser = new Parser(paths);
            parser.DoWork();
        }

        [Test]
        public void LogansRun_WithText()
        {
            var input = _input.Replace("\"\"", "\"");
            var grammar = _grammar.Replace("\"\"", "\"");
            var parser = new Parser(input, grammar);
            parser.DoWork();
        }
    }
}