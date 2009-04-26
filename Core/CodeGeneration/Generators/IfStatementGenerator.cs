using System.Collections.Generic;
using System.Text;
using bdUnit.Core.AST;
using bdUnit.Core.Templates;
using bdUnit.Core.Extensions;

namespace bdUnit.Core.Generators
{
    public class IfStatementGenerator : GeneratorBase
    {
        private readonly IAssertGenerator _assertGenerator;

        public IfStatementGenerator(IAssertGenerator assertGenerator)
        {
            _assertGenerator = assertGenerator as AssertGenerator;
        }

        public string Generate(If ifStatement)
        {
            object nestedIf = null;
            if (ifStatement.Else == null)
            {
                return TemplateIfStatement(ifStatement, null, false);
            }
            if (ifStatement.Else != null)
            {
                if (ifStatement.Else.If != null)
                {
                    nestedIf = Generate(ifStatement.Else.If);
                }
                return TemplateIfStatement(ifStatement, nestedIf, true);
            }
            return string.Empty;
        }

        private string TemplateIfStatement(If ifStatement, object nestedIfText, bool isNested)
        {
            var constraintText = new StringBuilder();
            var conditionText = string.Empty;
            ifStatement.Then.Constraints.ForEach(c =>
                                                     {
                                                         if (c.ConcreteClasses.Count > 0)
                                                         {
                                                             constraintText.Append(_assertGenerator.Generate(c.ConcreteClasses[0], new List<Constraint>{c}));
                                                         }
                                                         else if (c.Property != null)
                                                         {
                                                             constraintText.Append(_assertGenerator.Generate(c.Property.ConcreteClass, new List<Constraint> {c}));
                                                         }
                                                     });

            conditionText = BooleanGenerator.Generate(ifStatement.TargetList);
            var templateParams = new Dictionary<string, object>()
                                     {
                                         {"condition", conditionText},
                                         {"constraints", constraintText.ToString()},
                                         {"nestedIf", nestedIfText.ToString()},
                                         {"isNested", isNested}
                                     };
            return templateParams.AsNVelocityTemplate(TemplateEnum.IfElseStatement);
        }
    }
}