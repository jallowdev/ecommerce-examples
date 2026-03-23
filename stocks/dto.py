from typing import List

from ninja import Schema

from core.commons.dto import ModelOut

class ProductState(Schema):
    amountIn: int = 0
    amountOut: int = 0
    nbIn: int = 0
    nbOut: int = 0


class StateProduct:
    def __int__(self, amountIn: int = 0, amountOut: int = 0, nbIn: int = 0, nbOut: int = 0):
        self.amountIn = amountIn
        self.amountIn = amountOut
        self.nbIn = nbIn
        self.nbOut = nbOut


class ProductResponse(ModelOut):
    id: int = 0
    price: int = 0
    salePrice: int = 0
    quantity: int = 0
    sold: int = 0
    category: str = ''
    name: str = ''


class SaleRequest(Schema):
    id: int = 0
    identity: str = ''
    price: int = 0
    salePrice: int = 0
    quantity: int = 0
    sold: int = 0
    category: str = ''
    name: str = ''


class SaleRequests(Schema):
    customerId: int = 0
    storeId: str = None
    typeInvoice: str = 'FACTURE'
    requests: List[SaleRequest] = None
