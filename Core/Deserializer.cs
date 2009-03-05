#region Using Statements

using System;
using System.Collections.Generic;
using System.Dataflow;
using System.Linq;
using System.Reflection;
using bdUnit.Core.Utility;

#endregion

namespace bdUnit.Core
{
    public class Deserializer
    {
        private readonly GraphBuilder builder;

        public Deserializer()
        {
            builder = new GraphBuilder();
        }

        public object Deserialize(object node)
        {
            if (builder.IsSequence(node))
            {
                return DeserialzeSeq(node).ToList();
            }

            if (builder.IsNode(node))
            {
                return DeserializeNode(node);
            }

            return null;
        }

        private object DeserializeNode(object node)
        {
            var name = builder.GetLabel(node) as Identifier;

            foreach (object child in builder.GetSuccessors(node))
            {
                if (child is string)
                {
                    //Keep quotes for string values
                    if (name == "Value" && RegexUtility.IsString((string)child))
                    {
                        return child as string;
                    }
                    return UnQuote((string) child);
                }
            }

            var obj =
                Activator.CreateInstance(Assembly.GetExecutingAssembly().FullName, "bdUnit.Core.AST." + name.Text).Unwrap();

            InitializeObject(obj, node);

            return obj;
        }

        private void InitializeObject(object obj, object node)
        {
            foreach (object child in builder.GetSuccessors(node))
            {
                if (builder.IsSequence(child))
                {
                    foreach (object element in builder.GetSequenceElements(child))
                    {
                        AddToList(obj, child, element);
                    }
                }
                else if (builder.IsNode(child))
                {
                    obj.SetPropery(builder.GetLabel(child).ToString(), DeserializeNode(child));
                }
            }
        }

        private void AddToList(object obj, object parentNode, object element)
        {
            var propertyInfo = obj.GetType().GetProperty(builder.GetLabel(parentNode).ToString());
            var value = propertyInfo.GetValue(obj, null);
            var method = value.GetType().GetMethod("Add");
            method.Invoke(value, new[] {DeserializeNode(element)});
        }

        private IEnumerable<object> DeserialzeSeq(object node)
        {
            foreach (object element in builder.GetSequenceElements(node))
            {
                var obj = DeserializeNode(element);
                yield return obj;
            }
        }

        private object UnQuote(string str)
        {
            if (str.Contains("\""))
            {
                str = str.TrimStart('\"');
                str = str.TrimEnd('\"');
                return str;
            }
            if (str.Contains("#") || str.Contains("~") || str.Contains("@"))
            {
                return str.Substring(1, str.Length - 1);
            }
            return str;
        }
    }
}