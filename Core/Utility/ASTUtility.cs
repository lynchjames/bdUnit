#region Using Statements

using System.Collections.Generic;
using System.Linq;
using bdUnit.Core.AST;

#endregion

namespace bdUnit.Core.Utility
{
    public class ASTUtility
    {
        public static List<ConcreteClass> FindInstantiatedConcreteClasses(IStatement statement)
        {
            var list = new List<ConcreteClass>();
            //TODO Only using this for 'when' statements at the moment
            if (statement is When)
            {
                var whenStatement = statement as When;
                (whenStatement.TargetList).ForEach(t =>
                                                       {
                                                           if (t.TargetMethod != null)
                                                           {
                                                               list.AddRange(t.TargetMethod.ConcreteClasses);
                                                           }
                                                           if (t.TargetProperty != null)
                                                           {
                                                               list.AddRange(t.TargetProperty.ConcreteClasses);
                                                           }
                                                       });
                return list.Where(o => o.Instance.Value != null).Distinct(new ConcreteClassComparer()).ToList();
            }
            return list;
        }

        #region Nested type: ConcreteClassComparer

        public class ConcreteClassComparer : IEqualityComparer<ConcreteClass>
        {
            #region IEqualityComparer<ConcreteClass> Members

            public bool Equals(ConcreteClass x, ConcreteClass y)
            {
                return (x.Instance.Value == y.Instance.Value);
            }

            public int GetHashCode(ConcreteClass obj)
            {
                return obj.ToString().GetHashCode();
            }

            #endregion
        }

        #endregion
    }
}