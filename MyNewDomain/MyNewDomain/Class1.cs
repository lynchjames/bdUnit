﻿using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using bdUnit.Interfaces;
using StructureMap;

namespace MyNewDomain
{
    [Pluggable("bdUnit")]
    public class Car : ICar
    {
        public void Kill(ICar car)
        {
            throw new System.NotImplementedException();
        }

        public void Marry(ICar car)
        {
            throw new System.NotImplementedException();
        }

        public void Visit(IGarage garage)
        {
            throw new System.NotImplementedException();
        }

        public void Total()
        {
            throw new System.NotImplementedException();
        }

        public ICar Spouse
        {
            get { throw new System.NotImplementedException(); }
            set { throw new System.NotImplementedException(); }
        }

        public bool IsARunner
        {
            get { throw new System.NotImplementedException(); }
            set { throw new System.NotImplementedException(); }
        }

        public int Age
        {
            get { throw new System.NotImplementedException(); }
            set { throw new System.NotImplementedException(); }
        }

        public bool IsDead
        {
            get { throw new System.NotImplementedException(); }
            set { throw new System.NotImplementedException(); }
        }

        public IList<IUser> Children
        {
            get { throw new System.NotImplementedException(); }
            set { throw new System.NotImplementedException(); }
        }
    }

    [Pluggable("bdUnit")]
    public class User : IUser
    {
        // bdUnit
        [DefaultConstructor]
        public User()
        {
            Age = 21;
        }

        public User(string name)
        {
            Age = 13;
        }

        public IUser Spouse { get; set; }

        public bool IsARunner { get; set; }

        public int Age { get; set; }

        public bool IsDead { get; set; }

        public IList<IUser> Children { get; set; }

        public void Kill(IUser user)
        {
            user.IsDead = true;
        }

        public void Marry(IUser user)
        {
            this.Spouse = user;
            user.Spouse = this;
        }

        public void Visit(ISleepShop sleepshop)
        {
            this.IsDead = true;
        }

        public void Total()
        {
            throw new System.NotImplementedException();
        }
    }

    [Pluggable("bdUnit")]
    public class SleepShop : ISleepShop
    {
        public SleepShop()
        {

        }

        public ILocation Location { get; set; }

        public bool IsOpen { get; set; }

        public void Locate()
        {
            return;
        }
    }

    [Pluggable("bdUnit")]
    public class Location222 : ILocation
    {
        public decimal Latitude
        {
            get { throw new System.NotImplementedException(); }
            set { throw new System.NotImplementedException(); }
        }

        public decimal Longitude
        {
            get { throw new System.NotImplementedException(); }
            set { throw new System.NotImplementedException(); }
        }
    }
}