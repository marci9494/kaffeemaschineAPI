// Service.cs
using System;
using System.Collections.Generic;
using System.ServiceModel;
using System.ServiceModel.Description;
using System.ServiceModel.Web;
using System.Threading.Tasks;
using System.Text;
using Robot_Lib;
using EcoTalk_Lib;

namespace Kaffee
{
    [ServiceContract]
    public interface IService 
    {
        [OperationContract]
        [WebGet(ResponseFormat = WebMessageFormat.Json)]
        string sendCommand(string cmd);

        [OperationContract]
        [WebGet(ResponseFormat = WebMessageFormat.Json)]
        string getStatus();

        [OperationContract]
        [WebGet(ResponseFormat = WebMessageFormat.Json)]
        string doSomething(string cmd);

        [OperationContract]
        [WebInvoke]

        string EchoWithPost(string s);
    }
    public class Service :   CCommand, IService
    {
        public string sendCommand(string cmd)
        {
            // gültige cmds:
            // StartBeverage
            this.NotifyExecute(CStateType.Execute, cmd);
            this.NotifyExecute(CStateType.Execute, "WaitBeverage");


            return "sending command ...  " + cmd;
        }

        public string getStatus()
        {
            // gültige Rückgabewerte:
            // isRunning
            // timeout
            // ???

            object obj= UserDatabase.GetVar("coffee");

            return "making coffee ...  " + obj;
        }

        public string doSomething(string cmd)
        {
            return "Do something ...  " + cmd;
        }

        public string EchoWithPost(string s)
        {
            return "You said " + s;
        }
    }
    public class KaffeService
    {
         IFormInterface form;
         void service_task()
        {
            CCommand.OnExecute += new CCommand.CCommnadEvent(cmd_OnExecute);
            // Zugriff erlauben mit: netsh http add urlacl url=http://+:8000/ user=till
            WebServiceHost host = new WebServiceHost(typeof(Service), new Uri("http://localhost:8000/"));
            try
            {
                ServiceEndpoint ep = host.AddServiceEndpoint(typeof(IService), new WebHttpBinding(), "");
                host.Open();
                using (ChannelFactory<IService> cf = new ChannelFactory<IService>(new WebHttpBinding(), "http://localhost:8000"))
                {
                    cf.Endpoint.Behaviors.Add(new WebHttpBehavior());

                    IService channel = cf.CreateChannel();

                    string s;


                    Console.WriteLine("call http://localhost:8000/sendCommand?cmd=speak(args=\"Hello world\")");

                    Console.WriteLine("");

                }

                while (true)
                {
                    Task.Delay(10).Wait();
                }

                host.Close();
            }
            catch (CommunicationException cex)
            {
                Console.WriteLine("An exception occurred: {0}", cex.Message);
                host.Abort();
            }

        }

        public  void cmd_OnExecute(object sender, CCommandInfo moveInf)
        {
            Console.WriteLine("Webservice: "+ moveInf.sCommand);
            if(moveInf.state == CStateType.Execute)
             form.ExecuteCommand(sender, moveInf.sCommand);
        }

        public  void startService(IFormInterface form)
        {
            System.Threading.Thread myThread = new System.Threading.Thread(new
                System.Threading.ThreadStart(this.service_task));
            myThread.Start();
            //   form.ExecuteCommand(this, "");
            this.form = form;
            Task.Delay(1000).Wait();
            Console.WriteLine("Press <ENTER> to terminate");
            Console.ReadLine();

        }
    }
}
