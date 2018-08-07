using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading;
using System.Xml;
using EcoTalk_Lib;
using Robot_Lib;

namespace WMFCoffeeMaschine1500S
{
    public class CCoffeeMaschineCommand : CCommand
    {
        byte r, g, b;

        uint iBtnNbr = 2;
        uint iBarista = 1;
        uint iDecaf = 2;
        uint iSML = 1;
        uint iMilkType = 1;
        bool simState;

        bool cancelFlag { get; set; }
        uint timeout = 0;

        /// <summary>
        /// Instance der Kaffemaschine
        /// </summary>
        public static CWMFCoffeeMaschine coffeeMaschine;

        public static void SubscribeCommands()
        {
            sSubscribeCommands();
        }

        /// <summary>
        /// Anmelden der Befehle für diesn Modul
        /// </summary>
        public static void sSubscribeCommands()
        {
            CCommandTemplate.CommandsAdd("StartBeverage", typeof(CCoffeeMaschineCommand));
            CCommandTemplate.CommandsAdd("WaitBeverage", typeof(CCoffeeMaschineCommand));
            CCommandTemplate.CommandsAdd("SetLight", typeof(CCoffeeMaschineCommand));
            CCommandTemplate.CommandsAdd("WMFConnect", typeof(CCoffeeMaschineCommand));
        }

        public CCoffeeMaschineCommand()
        {
            
        }
        /// <summary>
        ///  Konstruktor mit Knoten
        /// </summary>
        /// <param name="xNode"></param>
        public CCoffeeMaschineCommand(XmlNode xNode)
        {
            node = xNode;
        }

        /// <summary>
        ///  Konstruktor mit Kommando und Dokument
        /// </summary>
        /// <param name="xNode"></param>
        public CCoffeeMaschineCommand(String szCommand, XmlDocument xDoc)
        {
            Init(xDoc, szCommand);
        }

        /// <summary>
        /// Vordefinition der Parameternamen.
        /// </summary>
        /// <param name="pCmd">Befehlsentwurf für diesen Befehl</param>
        /// <returns></returns>
        public override CCommandTemplate SetParName(CCommandTemplate pCmd)

        {

            try
            {
                String name = pCmd.code[0].ToString();
                switch (name)
                {
                    case "SetLight":
                        pCmd.pName.Add("r", new CParameterTemplate() { parType= typeof(int) }); pCmd.pName.Add("g", new CParameterTemplate() { parType= typeof(int) }); pCmd.pName.Add("b", new CParameterTemplate() { parType= typeof(int) }); 
                        pCmd.nTyp = CommandType.WMF;
                        break;
                    case "StartBeverage":
                        pCmd.pName.Add("BtnNbr", new CParameterTemplate() { parType= typeof(int) }); pCmd.pName.Add("Barista", new CParameterTemplate() { parType= typeof(int) }); pCmd.pName.Add("Decaf", new CParameterTemplate() { parType= typeof(int) }); pCmd.pName.Add("iSML", new CParameterTemplate() { parType= typeof(int) });
                        pCmd.pName.Add("iMilkType", new CParameterTemplate() { parType= typeof(int) });  pCmd.pName.Add("timeout", new CParameterTemplate() { parType= typeof(int) }); pCmd.pName.Add("simState", new CParameterTemplate() { parType= typeof(int) });
                        pCmd.nTyp = CommandType.WMF;
                        break;
                    case "WaitBeverage":
                        pCmd.pName.Add("timeout", new CParameterTemplate() { parType= typeof(int) });
                        pCmd.nTyp = CommandType.WMF;
                        break;
                    case "WMFConnect": 
                        pCmd.pName.Add("ip", new CParameterTemplate() { parType = typeof(string) });
                        pCmd.pName.Add("idle", new CParameterTemplate() { parType= typeof(int) });

                        pCmd.nTyp = CommandType.WMF;
                        break;

                }
                if (pCmd.Xmldoc != null)
                    pCmd.elem = pCmd.Xmldoc.CreateElement("Command");
                pCmd.isGroupNode = false;
            }
            catch (Exception ex)
            {
                MessageHandler.Error(null, 412, "kann keine Commandliste Auifbauen", ex);
                //throw;
            }
            return pCmd;
        }


        override public void Update(CProgramm mainPrg)
        {

            base.Update(mainPrg);
            MessageInfo mInfo = new MessageInfo(this, 416, MessageTyp.Info, "Update WMFCmd");
            mInfo.xml = node.OuterXml;
            mInfo.mType = MessageTyp.Message;
            mInfo.sCommand = this.ToString();
            MessageHandler.Message(mInfo);

            if (coffeeMaschine == null)
                coffeeMaschine = new CWMFCoffeeMaschine();

            try { 
            XmlElement xPar;
            mainPrg.SatzNum++;


                xPar = (XmlElement)node.SelectSingleNode("Par[@name='r']");
            if (xPar != null)
            {
                r = byte.Parse(xPar.InnerText, nfi);
                xPar.SetAttribute("typ", CommandType.Decimal.ToString());
            }
            xPar = (XmlElement)node.SelectSingleNode("Par[@name='g']");
            if (xPar != null)
            {
                g = byte.Parse(xPar.InnerText, nfi);
                xPar.SetAttribute("typ", CommandType.Decimal.ToString());
            }
            xPar = (XmlElement)node.SelectSingleNode("Par[@name='b']");
            if (xPar != null)
            {
                b = byte.Parse(xPar.InnerText, nfi);
                xPar.SetAttribute("typ", CommandType.Decimal.ToString());
            }
            xPar = (XmlElement)node.SelectSingleNode("Par[@name='timeout']");
            if (xPar != null)
            {
                timeout = uint.Parse(xPar.InnerText, nfi);
                xPar.SetAttribute("typ", CommandType.Decimal.ToString());
            }

            xPar = (XmlElement)node.SelectSingleNode("Par[@name='ip']");
            if (xPar != null)
            {
                int i = 0;
                if (coffeeMaschine.ipAdress == null)
                    coffeeMaschine.ipAdress = new byte[4];
                String[] substrings = xPar.InnerText.Split('.');
                foreach (var substring in substrings)
                {
                    coffeeMaschine.ipAdress[i++] = Convert.ToByte(substring);
                    Console.Write(Convert.ToByte(substring) + ".");
                }
                xPar.SetAttribute("typ", CommandType.Decimal.ToString());
            }

            xPar = (XmlElement)node.SelectSingleNode("Par[@name='BtnNbr']");
            if (xPar != null)
            {
                    if (uint.TryParse(UserDatabase.Evaluate(xPar.InnerText), out iBtnNbr))
                    {
                        // iBtnNbr = UInt16.Parse(xPar.InnerText, nfi);
                        xPar.SetAttribute("typ", CommandType.Decimal.ToString());
                    }
            }

            xPar = (XmlElement)node.SelectSingleNode("Par[@name='Barista']");
            if (xPar != null)
            {
                iBarista = UInt16.Parse(xPar.InnerText, nfi);
                xPar.SetAttribute("typ", CommandType.Decimal.ToString());
            }

            xPar = (XmlElement)node.SelectSingleNode("Par[@name='Decaf']");
            if (xPar != null)
            {
                iDecaf = UInt16.Parse(xPar.InnerText, nfi);
                xPar.SetAttribute("typ", CommandType.Decimal.ToString());
            }
            xPar = (XmlElement)node.SelectSingleNode("Par[@name='SML']");
            if (xPar != null)
            {
                iSML = UInt16.Parse(xPar.InnerText, nfi);
                xPar.SetAttribute("typ", CommandType.Decimal.ToString());
            }

            xPar = (XmlElement)node.SelectSingleNode("Par[@name='MilkType']");
            if (xPar != null)
            {
                iMilkType = UInt16.Parse(xPar.InnerText, nfi);
                xPar.SetAttribute("typ", CommandType.Decimal.ToString());
            }
            xPar = (XmlElement)node.SelectSingleNode("Par[@name='simState']");
            if (xPar != null)
            {
                simState = bool.Parse(xPar.InnerText);
                xPar.SetAttribute("typ", CommandType.Decimal.ToString());
            }

            }
            catch(Exception ex)
            {
                MessageHandler.Error(this, 41514,  "WMFS1500 can't update! ",ex);

            }
            if (!coffeeMaschine.isConnected)
            {
                if(coffeeMaschine.Connect() == 0)
                {
                    MessageHandler.Message(this, 4151, MessageTyp.Info, "WMFS1500 is connected");
                }
            }

        }


        override public void Execute(CProgramm mainPrg)
        {

            uint iret;
            MessageInfo mInfo = new MessageInfo(this, 416, MessageTyp.Info, "Execute WMFCmd");
            mInfo.xml = node.OuterXml;
            mInfo.mType = MessageTyp.Message;
            mInfo.sCommand = this.ToString();
            MessageHandler.Message(mInfo);

            

            Name = GetNodeName();
            //mainPrg.lineNr++;
            switch (Name)
            {
                case "SetLight":
                    iret= coffeeMaschine.setLightCode(r, g, b);
                    NotifyExecute(CStateType.Executed, "SetLight " + coffeeMaschine.setBeverageCode(iret));
                    break;
                case "StartBeverage":
                    iret = coffeeMaschine.setOrder(iBtnNbr, iBarista, iDecaf, iSML, iMilkType, simState);
                    NotifyExecute(CStateType.Executed, "StartBeverage " + coffeeMaschine.setBeverageCode(iret));
                    if(timeout==0) timeout = 90;
                   if( WaitBeverage(mainPrg))
                    MessageHandler.Message(this, 90, MessageTyp.Info, "Kaffemaschine fertig!");
                   else
                        MessageHandler.Warning(this, 90, "Kaffemaschine aborded!");

                    break;
                case "WaitBeverage":
                    if (timeout == 0) timeout = 90;
                    NotifyExecute(CStateType.Executed, "WaitBeverage " );
                    WaitBeverage(mainPrg);
                     

                    break;
                case "WMFConnect": // pCmd = new CommandTemplate(7);
                    iret = (uint)coffeeMaschine.Connect();
                    NotifyExecute(CStateType.Executed, "WMF Connected " + coffeeMaschine.setBeverageCode(iret));
                    break;

            }
        }


        /// <summary>
        /// wartet bis die Kaffezubereitung beendet ist
        /// </summary>
        /// <param name="mainPrg"></param>
        public bool WaitBeverage(CProgramm mainPrg) {
            int n = 0;
            UserDatabase.SetVar(this, "coffee", "start");
            Thread.Sleep(2500);
            while (coffeeMaschine.isBeverageRunning())
            {
                uint err = coffeeMaschine.cm.isErrorActive();
                UserDatabase.SetVar(this, "coffee", "isRunning");                
                Thread.Sleep(500);
                if (mainPrg.prgStopFlag) {
                    return false; 
                }
                if (cancelFlag) {
                    cancelFlag = false;
                    return false; 
                }
                if (n++ > 2 * timeout)
                {
                    MessageHandler.Error(this, 90, "Timeout Kaffemaschine");
                    UserDatabase.SetVar(this, "coffee", "timeout");
                    return false;
                }

            }
            UserDatabase.SetVar(this, "coffee", "ready");
            return true;

        }

        public delegate void CCommnadEvent(object sender, CCommandInfo coffeeInf);
        public static event CCommnadEvent OnExecute;

        public void NotifyExecute(CStateType cmdState, String cmd)
        {
            if (OnExecute != null)
            {
                CCommandInfo cmdInfo = new CCommandInfo(cmd);
                cmdInfo.Message = cmd;
                cmdInfo.cmd = this;
                cmdInfo.xNode = node;
                cmdInfo.state = cmdState;
                OnExecute(this, cmdInfo);

            }
        }


    }
}
