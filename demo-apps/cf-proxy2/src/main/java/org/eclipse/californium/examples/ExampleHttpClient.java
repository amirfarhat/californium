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
    String destinationHostIn = null;
    int destinationPortIn = -1;
    int logStartWindowIn = -1;
    int logEndWindowIn = -1;

    if (args.length != 4) {
      System.err.println("Need [destinationHost] [destinationPort] [logStartWindow] [logEndWindow]");
      System.exit(1);
    } else {
      destinationHostIn = args[0];
      destinationPortIn = Integer.parseInt(args[1]);
      logStartWindowIn = Integer.parseInt(args[2]);
      logEndWindowIn = Integer.parseInt(args[3]);
      if (logEndWindowIn < logStartWindowIn) {
        throw new RuntimeException("Bad args");
      }
    }

    final String destinationHost = destinationHostIn;
    final int destinationPort = destinationPortIn;
    final int startWindow = (int) Math.pow(2, logStartWindowIn);
    final int endWindow = (int) Math.pow(2, logEndWindowIn);
    
    httpHost = new HttpHost(destinationHost, destinationPort);
    httpRequest = new HttpGet("http://" + destinationHost + ":" + destinationPort);

    int n = startWindow;
    while (n < endWindow) {
      System.out.println("==================== " + n);

      latch = new CountDownLatch(n);
      for (int i = 0; i < n; i++) {
        sendRequest(i);
      }
      latch.await();

      n *= 2;
    }
    
    System.exit(0);
	}
}
