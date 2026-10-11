package com.deadzone.esports;

import org.springframework.boot.SpringApplication;

public class TestDeadzoneEsportsApplication {

	public static void main(String[] args) {
		SpringApplication.from(DeadzoneEsportsApplication::main).with(TestcontainersConfiguration.class).run(args);
	}

}
