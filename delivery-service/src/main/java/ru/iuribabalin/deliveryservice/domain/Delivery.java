package ru.iuribabalin.deliveryservice.domain;

import java.time.LocalDateTime;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.Table;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import lombok.ToString;

/**
 * @author Iurii Babalin (ueretz)
 */
@Getter
@Setter
@Entity
@AllArgsConstructor
@NoArgsConstructor
@ToString(of = "id")
@Table(name = "delivery")
public class Delivery {
    @Id
    private String id;
    @ManyToOne
    @JoinColumn(name = "deliveryman_id")
    private Deliveryman deliveryman;
    @Column(name = "order_id")
    private String orderId;
    @Column(name = "order_date_created")
    private LocalDateTime orderDateCreated;
    @Column(name = "delivery_address")
    private String deliveryAddress;
    @Column(name = "delivery_time")
    private LocalDateTime deliveryTime;
    private Integer rating;
    private Long tips;
}
