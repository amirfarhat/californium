/*******************************************************************************
 * Copyright (c) 2020 Bosch IO GmbH and others.
 * 
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v2.0
 * and Eclipse Distribution License v1.0 which accompany this distribution.
 * 
 * The Eclipse Public License is available at
 *    http://www.eclipse.org/legal/epl-v20.html
 * and the Eclipse Distribution License is available at
 *    http://www.eclipse.org/org/documents/edl-v10.html.
 * 
 * Contributors:
 *    Bosch IO GmbH - initial implementation
 ******************************************************************************/

package org.eclipse.californium.examples;

import java.io.IOException;
import java.net.InetSocketAddress;
import java.util.concurrent.TimeUnit;

import org.eclipse.californium.core.CoapClient;
import org.eclipse.californium.core.CoapResponse;
import org.eclipse.californium.core.coap.CoAP.Type;
import org.eclipse.californium.core.coap.MediaTypeRegistry;
import org.eclipse.californium.core.coap.Request;
import org.eclipse.californium.elements.AddressEndpointContext;
import org.eclipse.californium.elements.exception.ConnectorException;
import org.eclipse.californium.proxy2.resources.ProxyHttpClientResource;

/**
 * Class ExampleProxyCoapClient. <br/>
 * Example CoAP client which sends a request to Proxy Coap server with a
 * {@link ProxyHttpClientResource} to get the response from HttpServer. <br/>
 * 
 * For testing Coap2Http:<br/>
 * Destination: localhost:5683 (proxy's address)<br/>
 * Coap Uri: {@code coap://localhost:8000/http-target}<br/>
 * Proxy Scheme: {@code http}.
 * 
 * or <br/>
 * 
 * Destination: localhost:5683 (proxy's address)<br/>
 * Proxy Uri: {@code http://user@localhost:8000/http-target}.<br/>
 * 
 * For testing Coap2coap: <br/>
 * Destination: localhost:5683 (proxy's address)<br/>
 * Coap Uri: {@code coap://localhost:5685/coap-target}.<br/>
 * 
 * Deprecated modes:<br/>
 * Uri: {@code coap://localhost:8000/coap2http}. <br/>
 * Proxy Uri: {@code http://localhost:8000/http-target}.<br/>
 * 
 * For testing Coap2coap: <br/>
 * Uri: {@code coap://localhost:5683/coap2coap}. <br/>
 * Proxy Uri: {@code coap://localhost:5685/coap-target}.<br/>
 * 
 */
public class ExampleProxy2CoapClient {

	private static final int PROXY_PORT = 5683;

	private static String request(CoapClient client, Request request) {
		try {
			CoapResponse response = client.advanced(request);
			String midTok = response.advanced().getMID() + "_" + response.advanced().getTokenString();
			return midTok;
		} catch (ConnectorException | IOException e) {
			throw new RuntimeException(e);
		}
	}

	public static void main(String[] args) throws InterruptedException {
		if (args.length != 2) {
			System.out.println("Args [proxy url] [dest url]");
			System.exit(1);
		}
		String proxyUri = args[0];
		String destinationUri = args[1];

		CoapClient client = new CoapClient();
		client.useCONs();

		String midTok;
		Request request;
		long start;
		
		for (int i = 0; i < 1000; i++) {
			request = Request.newGet();
			request.setURI(proxyUri);
			request.getOptions().setProxyUri(destinationUri);

			start = System.nanoTime();
			midTok = request(client, request);
			System.out.println(midTok + ": " + (System.nanoTime() - start) + " ns");
			
			TimeUnit.SECONDS.sleep(1);
		}

		client.shutdown();
	}
}