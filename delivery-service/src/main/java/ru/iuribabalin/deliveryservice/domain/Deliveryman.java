package ru.iuribabalin.deliveryservice.domain;

import java.util.List;

import jakarta.persistence.CascadeType;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.OneToMany;
import jakarta.persistence.Table;
import lombok.Getter;
import lombok.Setter;
import lombok.ToString;

/**
 * @author Iurii Babalin (ueretz)
 */
@Getter
@Setter
@Entity
@ToString(of = "id")
@Table(name = "deliveryman")
public class Deliveryman {
    @Id
    private String id;

    private String name;

    @OneToMany(mappedBy = "deliveryman", cascade = CascadeType.ALL)
    private List<Delivery> deliveryList;

}
