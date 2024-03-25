package com.unipu.smart_parksystem.entity;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import javax.persistence.Entity;
import javax.persistence.GeneratedValue;
import javax.persistence.GenerationType;
import javax.persistence.Id;
import java.sql.Timestamp;

@Entity
@Data
@AllArgsConstructor
@NoArgsConstructor
@Builder
public class Transaction {

    @Id
    @GeneratedValue(
            strategy = GenerationType.SEQUENCE
    )
    private Long transactionId;
    private Long amount;
    private Long ticketId;
    private Timestamp created;
    private Timestamp modified;



}
