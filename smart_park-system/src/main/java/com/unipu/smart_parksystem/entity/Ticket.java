package com.unipu.smart_parksystem.entity;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import javax.persistence.*;
import java.awt.*;
import java.sql.Timestamp;


@Entity
@Data
@AllArgsConstructor
@NoArgsConstructor
@Builder
@Table(name = "tbl_ticket",
        uniqueConstraints = @UniqueConstraint(
                name = "ticketId_unique",
                columnNames = "ticket_id"
        ))

public class Ticket {


    @Id
    @Column(
            name = "ticket_id",
            nullable = false
    )
    @GeneratedValue(strategy = GenerationType.SEQUENCE)
    private Long ticketId;
    private String registration;
    private Timestamp timeOfEnter;
    private Timestamp timeOfExit;
    private Double price;
    private Timestamp exitTimeout;
    private boolean created;
    private String modified;



}
