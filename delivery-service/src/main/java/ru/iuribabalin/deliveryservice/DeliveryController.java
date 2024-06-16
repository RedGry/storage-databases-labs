package ru.iuribabalin.deliveryservice;

import java.util.List;

import lombok.AllArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import ru.iuribabalin.deliveryservice.model.CreateDelivery;
import ru.iuribabalin.deliveryservice.model.DeliveryDto;
import ru.iuribabalin.deliveryservice.model.DeliverymanDto;
import ru.iuribabalin.deliveryservice.service.DeliveryService;

/**
 * @author Iurii Babalin (ueretz)
 */
@RestController
@RequestMapping("/delivery")
@AllArgsConstructor
public class DeliveryController {

    private final DeliveryService deliveryService;

    @PostMapping
    public DeliveryDto createDelivery(@RequestBody CreateDelivery createDelivery) {
        return deliveryService.createDeliveryForDeliveryman(createDelivery);
    }

    @GetMapping("/deliverers")
    public List<DeliverymanDto> getDeliverers(@RequestParam Long limit, @RequestParam Long page) {
        return deliveryService.getDeliverers(limit, page);
    }

    @GetMapping("/deliveryman/{deliverymanId}")
    public List<DeliveryDto> getDeliveryForDeliveryman(@PathVariable String deliverymanId) {
        return deliveryService.getDeliveryForDeliveryman(deliverymanId);
    }
}
