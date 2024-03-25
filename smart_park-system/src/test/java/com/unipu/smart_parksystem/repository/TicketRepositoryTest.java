package com.unipu.smart_parksystem.repository;

import com.unipu.smart_parksystem.entity.Ticket;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

import java.awt.*;
import java.sql.Timestamp;
import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;

import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest
class TicketRepositoryTest {

    LocalDateTime timeOfEnter = LocalDateTime.now();
    LocalDateTime timeOfExit = timeOfEnter.plus(50, ChronoUnit.MINUTES);

    double pricePerMinute = 0.02;
    long minutesDifference = ChronoUnit.MINUTES.between(timeOfEnter, timeOfExit);
    double totalPrice = minutesDifference * pricePerMinute;

    LocalDateTime timeOfExitTimeout = timeOfExit.plusMinutes(15);


    @Autowired
    private TicketRepository ticketRepository;

    @Test
    public void saveTicket(){
        Ticket ticket = Ticket
                .builder()
                .registration("zg184pj")
                .timeOfEnter(Timestamp.valueOf(timeOfEnter))
                .timeOfExit(Timestamp.valueOf(timeOfExit))
                .price(totalPrice)
                .exitTimeout(Timestamp.valueOf(timeOfExitTimeout))
                .created(true)
                .build();

        ticketRepository.save(ticket);
    }
//
//    private Long ticketId;
//    private String registration;
//    private Timestamp timeOfEnter;
//    private Timestamp timeOfExit;
//    private Long price;
//    private Timestamp exitTimeout;
//    private Checkbox created;
//    private String modified;
}