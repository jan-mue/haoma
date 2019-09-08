using System;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Threading.Tasks;
using System.Web;

namespace Techfest.Helpers
{
    public class HttpBuilder
    {
        private const string baseUri = "http://10.25.13.227:5000/patient";
        private WebClient client;
        private string uri;

        public HttpBuilder()
        {
            client = new WebClient();
            client.BaseAddress = baseUri;
        }
        public string GetResponse(string id)
        {
            client = BuildGetRequest(id);
            return this.client.DownloadString(uri);
        }

        public WebClient BuildGetRequest(string id)
        {
            uri = BuildUri(id);
            client.BaseAddress = baseUri;
            client.Headers.Add(HttpRequestHeader.ContentType, "application/x-www-form-urlencoded");
            return client;
        }

        private static string BuildUri(string id)
        {
            UriBuilder uriBuilder = new UriBuilder(baseUri);
            uriBuilder.Port = 5000;
            var query = HttpUtility.ParseQueryString(uriBuilder.Query);
            query["patient_key"] = id;
            uriBuilder.Query = query.ToString();
            return uriBuilder.ToString();
        }
    }
}