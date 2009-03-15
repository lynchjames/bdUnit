using System.Collections.Generic;
using bdUnit.Core.AST;
using System.Linq;

namespace bdUnit.Core.Utility
{
    public class ASTUtility
    {
        public static List<Object> FindInstantiatedObjects(IStatement statement)
        {
            var list = new List<Object>();
            //TODO Only using this for 'when' statements at the moment
            if (statement is When)
            {
                var whenStatement = statement as When;
                ((List<Target>)whenStatement.TargetList).ForEach(t =>
                                                                     {
                                                                         if (t.TargetMethod != null)
                                                                         {
                                                                             list.AddRange(t.TargetMethod.Objects);
                                                                         }
                                                                         if (t.TargetProperty != null)
                                                                         {
                                                                             list.AddRange(t.TargetProperty.Objects);
                                                                         }
                                                                     });
                return list.Where(o => o.Instance.Value != null).Distinct(new ObjectComparer()) .ToList();
            }
            return list;
        }

        public class ObjectComparer : IEqualityComparer<Object>
        {
            public bool Equals(Object x, Object y)
            {
                return (x.Instance.Value == y.Instance.Value);

            }

            public int GetHashCode(Object obj)
            {
                return obj.ToString().GetHashCode();
            }
        }
    }
}