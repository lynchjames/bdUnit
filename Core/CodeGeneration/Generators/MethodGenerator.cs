#region Using Statements

using System.Collections.Generic;
using System.Text;
using bdUnit.Core.AST;
using bdUnit.Core.Extensions;
using bdUnit.Core.Templates;

#endregion

namespace bdUnit.Core.Generators
{
    public interface IMethodGenerator
    {
        StringBuilder Generate(List<IStatement> statements, StringBuilder stringBuilder);
    }

    public class MethodGenerator : GeneratorBase, IMethodGenerator
    {
        private readonly IAssertGenerator _assertGenerator;

        public MethodGenerator(IAssertGenerator assertGenerator, string testText)
        {
            _assertGenerator = assertGenerator as AssertGenerator;
            TestText = testText;
        }

        #region IMethodGenerator Members

        public StringBuilder Generate(List<IStatement> statements, StringBuilder stringBuilder)
        {
            var statementCount = statements.Count;
            if (statementCount > 0)
            {
                for (var i = 0; i < statementCount; i++)
                {
                    var statement = statements[i];
                    var whenStatement = statement as When;
                    if (whenStatement == null) continue;
                    if (whenStatement.TargetList.Count > 1)
                    {
                        stringBuilder = GenerateForTargets(whenStatement.TargetList, stringBuilder);
                    }
                    else
                    {
                        var target = whenStatement.TargetList[0];
                        if (target.TargetProperty != null)
                        {
                            stringBuilder = GenerateForTargetProperty(target.TargetProperty, stringBuilder);
                        }
                        else
                        {
                            var variables = new StringBuilder();
                            stringBuilder = GenerateForTargetMethod(target.TargetMethod, variables, whenStatement,
                                                                    stringBuilder);
                        }
                    }
                    (whenStatement.Constraints).ForEach(c =>
                                                            {
                                                                if (c.ConcreteClasses.Count > 0)
                                                                {
                                                                    stringBuilder.Append(
                                                                        _assertGenerator.Generate(c.ConcreteClasses[0],
                                                                                                  new List<Constraint>
                                                                                                      {c}));
                                                                }
                                                                else if (c.Property != null)
                                                                {
                                                                    stringBuilder.Append(
                                                                        _assertGenerator.Generate(
                                                                            c.Property.ConcreteClass,
                                                                            new List<Constraint> {c}));
                                                                }
                                                            });
                    _assertGenerator.GenerateForLoop(whenStatement, stringBuilder);
                    stringBuilder.AppendLine("\t\t}");
                }
            }
            return stringBuilder;
        }

        #endregion

        private StringBuilder GenerateForTargets(List<Target> list, StringBuilder stringBuilder)
        {
            var titleSet = false;
            var previouslyCreated = new List<string>();
            list.ForEach(x =>
                             {
                                 if (x.TargetProperty != null)
                                 {
                                     var property = x.TargetProperty;
                                     var obj = property.ConcreteClasses[0];
                                     if (!titleSet)
                                     {
                                         var title = string.Format("When_{0}_Is_Set_...", property.Name);
                                         stringBuilder.AppendLine(TestText.Replace("##testname##", title));
                                         stringBuilder.AppendLine("\t\t{");
                                         titleSet = true;
                                     }
                                     if (!previouslyCreated.Contains(obj.Instance.Value))
                                     {
                                         stringBuilder.AppendLine(
                                             obj.AsNVelocityTemplate(TemplateEnum.StructureMapInstance));
                                         previouslyCreated.Add(obj.Instance.Value);
                                     }
                                     stringBuilder.AppendLine(string.Format("\t\t\t{0}.{1} {2} {3};", obj.Instance.Value,
                                                                            property.Name,
                                                                            property.Operators[0].Value.Replace("==",
                                                                                                                "="),
                                                                            property.Value));
                                 }
                                 else
                                 {
                                     var target = x.TargetMethod;
                                     var objects = target.ConcreteClasses;
                                     var obj = objects[0];
                                     var otherObj = objects[1];
                                     var variables = new StringBuilder();
                                     if (!previouslyCreated.Contains(obj.Instance.Value))
                                     {
                                         variables.Append(obj.AsNVelocityTemplate(TemplateEnum.StructureMapInstance));
                                         previouslyCreated.Add(obj.Instance.Value);
                                     }
                                     if (!previouslyCreated.Contains(otherObj.Instance.Value))
                                     {
                                         variables.Append(otherObj.AsNVelocityTemplate(TemplateEnum.StructureMapInstance));
                                         previouslyCreated.Add(otherObj.Instance.Value);
                                     }
                                     var methodUsage = string.Format("\t\t\t{0}.{1}({2});\n", obj.Instance.Value,
                                                                        target.Name,
                                                                        otherObj.Instance.Value);

                                     if (!titleSet)
                                     {
                                         var title = string.Format("When_{0}_{1}_{2}", obj.Name, target.Name,
                                                                      otherObj.Name);
                                         stringBuilder.AppendLine(TestText.Replace("##testname##", title));
                                         stringBuilder.AppendLine("\t\t{");
                                         titleSet = true;
                                     }
                                     stringBuilder.Append(variables).Append(methodUsage);
                                 }
                             });
            return stringBuilder;
        }

        //TODO Need to be able to test the returned object from a method?
        private StringBuilder GenerateForTargetProperty(TargetProperty property, StringBuilder stringBuilder)
        {
            var obj = property.ConcreteClasses[0];
            var title = string.Format("When_{0}_{1}_Is_Set", obj.Name, property.Name);
            stringBuilder.AppendLine(TestText.Replace("##testname##", title));
            stringBuilder.AppendLine("\t\t{");
            stringBuilder.AppendLine(obj.AsNVelocityTemplate(TemplateEnum.StructureMapInstance));
            stringBuilder.AppendLine(string.Format("\t\t\t{0}.{1} {2} {3};", obj.Instance.Value, property.Name,
                                                   property.Operators[0].Value.Replace("==", "="), property.Value));
            //stringBuilder.Append(Generate(property));
            return stringBuilder;
        }

        private StringBuilder GenerateForTargetMethod(ITarget target, StringBuilder variables, When whenStatement,
                                                      StringBuilder stringBuilder)
        {
            var objects = target.ConcreteClasses;
            var obj = objects[0];
            var otherObj = objects[1];
            variables.Append(obj.AsNVelocityTemplate(TemplateEnum.StructureMapInstance));
            variables.Append(otherObj.AsNVelocityTemplate(TemplateEnum.StructureMapInstance));
            var methodUsage = string.Format("\t\t\t{0}.{1}({2});\n", obj.Instance.Value, target.Name,
                                               otherObj.Instance.Value);

            //TODO: Add logic to determine type constuctor @User(Name = Jim, Age = 25) should correspond to var Jim = new User() {Name = "Jim", Age = 25};
            var title = string.Format("When_{0}_{1}_{2}", obj.Name, target.Name, otherObj.Name);
            stringBuilder.AppendLine(TestText.Replace("##testname##", title));
            stringBuilder.AppendLine("\t\t{");
            stringBuilder.Append(variables).Append(methodUsage);
            return stringBuilder;
        }
    }
}