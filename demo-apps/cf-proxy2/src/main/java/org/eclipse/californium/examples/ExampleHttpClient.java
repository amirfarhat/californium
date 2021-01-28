package org.eclipse.californium.examples;

import java.util.concurrent.CountDownLatch;

import javax.sound.midi.SysexMessage;

import org.apache.http.HttpHost;
import org.apache.http.HttpRequest;
import org.apache.http.HttpResponse;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.concurrent.FutureCallback;
import org.apache.http.impl.nio.client.CloseableHttpAsyncClient;
import org.eclipse.californium.proxy2.HttpClientFactory;

public class ExampleHttpClient {
  private static final CloseableHttpAsyncClient asyncClient = HttpClientFactory.createClient();  
  private static HttpHost httpHost;
  private static HttpRequest httpRequest;
  private static CountDownLatch latch;

  private static void sendRequest(int i) {
    final int j = i;
    System.out.println("REQ " + i + " " + System.nanoTime());

    asyncClient.execute(httpHost, httpRequest, new FutureCallback<HttpResponse>(){
      @Override
      public void completed(HttpResponse result) {
        System.out.println("Y RES " + j + " " + System.nanoTime());
        latch.countDown();
      }
      @Override
      public void failed(Exception e) {
        System.out.println("N RES " + j + " " + System.nanoTime());
        latch.countDown();
      }
      @Override
      public void cancelled() {
        System.out.println("N RES " + j + " " + System.nanoTime());
        latch.countDown();
      }
    });
  }

  public static void main(String args[]) throws InterruptedException {
    // final int n = Integer.parseInt(args[0]);
    int n = 1;

    final String destinationHost = "127.0.0.1";
    final int destinationPort = 8000;
    
    httpHost = new HttpHost(destinationHost, destinationPort);
    httpRequest = new HttpGet("http://" + destinationHost + ":" + destinationPort);

    for (int k = 0; k < 1000; k++) {
      if (n == 262144) {
        System.exit(0);
      }
      System.out.println("==================== " + n);
      latch = new CountDownLatch(n);
      for (int i = 0; i < n; i++) {
        sendRequest(i);
      }
      latch.await();
      n *= 2;
    }
	}
}
