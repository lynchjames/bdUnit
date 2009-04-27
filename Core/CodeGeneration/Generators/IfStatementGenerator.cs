using System;
using System.Collections.Generic;
using System.Text;
using bdUnit.Core.AST;
using bdUnit.Core.Templates;
using bdUnit.Core.Extensions;

namespace bdUnit.Core.Generators
{
    public interface IIfStatementGenerator
    {
        string GenerateRecursive(If ifStatement, ref StringBuilder builder);
    }

    public class IfStatementGenerator : GeneratorBase, IIfStatementGenerator
    {
        private readonly IAssertGenerator _assertGenerator;
        private readonly IBooleanGenerator _booleanGenerator;

        public IfStatementGenerator(IAssertGenerator assertGenerator)
        {
            _assertGenerator = assertGenerator as AssertGenerator;
            _booleanGenerator = new BooleanGenerator();
        }

        public string GenerateRecursive(If ifStatement, ref StringBuilder builder)
        {
            object nestedIf = null;
            if (ifStatement.Else == null)
            {
                return TemplateIfStatement(ifStatement, null, false, ref builder);
            }
            if (ifStatement.Else != null)
            {
                if (ifStatement.Else.If != null)
                {
                    nestedIf = GenerateRecursive(ifStatement.Else.If, ref builder);
                }
                return TemplateIfStatement(ifStatement, nestedIf, true, ref builder);
            }
            return string.Empty;
        }

        private string TemplateIfStatement(If ifStatement, object nestedIfText, bool isNested, ref StringBuilder builder)
        {
            var constraintText = new StringBuilder();
            var elseConstraintText = new StringBuilder();
            var conditionText = string.Empty;
            
            conditionText = _booleanGenerator.Generate(ifStatement.TargetList, ref builder);
            constraintText = GenerateConstraints(ifStatement.Then.Constraints, constraintText);
            elseConstraintText = GenerateConstraints(ifStatement.Else.Constraints, elseConstraintText);

            var templateParams = new Dictionary<string, object>()
                                     {
                                         {"condition", conditionText},
                                         {"constraints", constraintText.ToString()},
                                         {"nestedIf", nestedIfText},
                                         {"hasNestedIf", nestedIfText != null},
                                         {"isNested", isNested},
                                         {"elseConstraints", elseConstraintText}
                                     };
            return templateParams.AsNVelocityTemplate(TemplateEnum.IfElseStatement);
        }

        private StringBuilder GenerateConstraints(List<Constraint> constraints, StringBuilder constraintText)
        {
            constraints.ForEach(c =>
            {
                if (c.ConcreteClasses.Count > 0)
                {
                    constraintText.Append(_assertGenerator.Generate(c.ConcreteClasses[0], new List<Constraint> { c }));
                }
                else if (c.Property != null)
                {
                    constraintText.Append(_assertGenerator.Generate(c.Property.ConcreteClass, new List<Constraint> { c }));
                }
            });
            return constraintText;
        }
    }
}